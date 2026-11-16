#!/usr/bin/env bash
# ==========================================================================================
# A-23 REQUEST-WORDING CONTROLS ONLY — reviewer-4 response run (2026-11)
#
# Runs ONLY the three request-wording controls (neutral / goldcue / neutral_disclosed)
# on exactly the 13 serving labels that carry a trap measurement (results/masked/*.json),
# so the output lines up one-to-one with the concealed/disclosed/placebo baselines.
#
# Deliberately EXCLUDED (they belong to the separate v28 INT8 agenda, not to this question):
#   - the 216-task base runs, the placebo run, the logit probes
#   - the Llama-3.1 cells (they carry no trap baseline)
#   - the TP=2 cells, so a SINGLE A100-80GB is enough for every cell here
#
#   PASS A (Qwen2.5):  bash bootstrap_fp16.sh && bash run_a23_controls.sh a
#   PASS B (Qwen3):    pip install "vllm==0.8.5" "transformers==4.51.3" "numpy<2" && bash run_a23_controls.sh b
#
# Volume: Qwen2.5-32B-fp16 (~65 GB) and Qwen3-32B-fp16 (~65 GB) need room. Either attach a
#   >=300 GB network volume, or run with CLEAR_CACHE=1 to drop each model after its cell.
# Retrieve: tar czf a23_controls.tgz results/v28/controls results/v28_recipe logs && runpodctl send a23_controls.tgz
# Then, with no GPU:  python a25_v28_aggregate.py   ->  results/v28/A25_summary.md
# ==========================================================================================
set -uo pipefail
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://localhost:8000/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-dummy}"
export HF_HOME="${HF_HOME:-/workspace/hf-cache}"
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
REPEATS="${REPEATS:-3}"
PASS="${1:?usage: run_a23_controls.sh <a|b>}"
mkdir -p logs results/v28/controls results/v28_recipe "$HF_HOME"

# served | hf_id | parser | quant | tp | vllm flags | nothink
CELLS_A=(
  "qwen2.5-7b|Qwen/Qwen2.5-7B-Instruct|hermes|fp16|1|--dtype float16|0"
  "qwen2.5-7b|Qwen/Qwen2.5-7B-Instruct-GPTQ-Int8|hermes|int8|1|--quantization gptq_marlin|0"
  "qwen2.5-7b|Qwen/Qwen2.5-7B-Instruct-AWQ|hermes|int4|1|--quantization awq|0"
  "qwen2.5-32b|Qwen/Qwen2.5-32B-Instruct|hermes|fp16|1|--dtype float16|0"
  "qwen2.5-32b|Qwen/Qwen2.5-32B-Instruct-GPTQ-Int8|hermes|int8|1|--quantization gptq_marlin|0"
  "qwen2.5-32b|Qwen/Qwen2.5-32B-Instruct-AWQ|hermes|int4|1|--quantization awq|0"
  "qwen2.5-72b|Qwen/Qwen2.5-72B-Instruct-AWQ|hermes|int4|1|--quantization awq|0"
)
CELLS_B=(
  "qwen3-8b|Qwen/Qwen3-8B|hermes|fp16|1|--dtype float16|1"
  "qwen3-8b|Qwen/Qwen3-8B-AWQ|hermes|int4|1|--quantization awq|1"
  "qwen3-14b|Qwen/Qwen3-14B|hermes|fp16|1|--dtype float16|1"
  "qwen3-14b|Qwen/Qwen3-14B-AWQ|hermes|int4|1|--quantization awq|1"
  "qwen3-32b|Qwen/Qwen3-32B|hermes|fp16|1|--dtype float16|1"
  "qwen3-32b|Qwen/Qwen3-32B-AWQ|hermes|int4|1|--quantization awq|1"
)
if [[ "$PASS" == "a" ]]; then CELLS=("${CELLS_A[@]}"); else CELLS=("${CELLS_B[@]}"); fi

free_gpu() {
  pkill -INT -f "vllm.entrypoints" 2>/dev/null || true; sleep 8
  for pid in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | tr -d ' '); do kill -9 "$pid" 2>/dev/null || true; done
  sleep 3
}
trap free_gpu EXIT

# gate: the corpus controls must be lexically clean before any GPU time is spent
python a23_request_controls.py --self-test >/dev/null || { echo "!! a23 self-test failed"; exit 1; }
echo "== a23 self-test OK =="

done_n=0; fail_n=0
for cell in "${CELLS[@]}"; do
  IFS='|' read -r NAME HFID PARSER QUANT TP FLAGS NOTHINK <<< "$cell"
  STEM="${NAME}_${QUANT}"
  if [[ -s "results/v28/controls/neutral/${STEM}.json" \
     && -s "results/v28/controls/goldcue/${STEM}.json" \
     && -s "results/v28/controls/neutral_disclosed/${STEM}.json" ]]; then
    echo "== skip $STEM (all three conditions present) =="; done_n=$((done_n+1)); continue
  fi
  echo "================ $STEM ================"
  SLOG="logs/ctrl_serve_${STEM}.log"
  ./serve_vllm.sh "$HFID" "$NAME" "$PARSER" "$TP" $FLAGS > "$SLOG" 2>&1 &
  SPID=$!
  ready=""
  for _ in $(seq 1 400); do
    curl -sf "$OPENAI_BASE_URL/models" >/dev/null 2>&1 && { ready=1; break; }
    kill -0 "$SPID" 2>/dev/null || { echo "!! server exited early -> $SLOG"; break; }
    sleep 3
  done
  if [[ -z "$ready" ]]; then echo "!! $STEM never became ready"; fail_n=$((fail_n+1)); free_gpu; continue; fi

  NT=""; [[ "$NOTHINK" == "1" ]] && NT="--no-think"
  OUTS=()
  for C in neutral goldcue neutral_disclosed; do
    if python a23_request_controls.py --condition "$C" --model "$HFID" --served-name "$NAME" \
         --quant "$QUANT" --repeats "$REPEATS" $NT --out "results/v28/controls/${C}/${STEM}.json"; then
      OUTS+=("results/v28/controls/${C}/${STEM}.json")
    else
      echo "!! $STEM condition $C failed"; fail_n=$((fail_n+1))
    fi
  done
  # serving provenance for Supplementary S3, same as the v28 session
  [[ ${#OUTS[@]} -gt 0 ]] && python capture_serving_recipe.py --served "$NAME" --quant "$QUANT" \
      --hf-id "$HFID" --flags "$FLAGS" --server-log "$SLOG" --results "${OUTS[@]}"
  [[ ${#OUTS[@]} -eq 3 ]] && done_n=$((done_n+1))

  kill -INT "$SPID" 2>/dev/null || true; wait "$SPID" 2>/dev/null || true
  free_gpu
  [[ "${CLEAR_CACHE:-0}" == "1" ]] && rm -rf "$HF_HOME"/hub/models--"${HFID//\//--}" 2>/dev/null || true
done

echo "== PASS $PASS DONE ==  cells complete: $done_n / ${#CELLS[@]}   failures: $fail_n"
echo "   next (no GPU):  python a25_v28_aggregate.py   ->  results/v28/A25_summary.md"
