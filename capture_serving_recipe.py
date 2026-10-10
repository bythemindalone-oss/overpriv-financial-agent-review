#!/usr/bin/env python3
"""A-24 (v28) — record, WHILE the server is up, what vLLM actually loaded.

v27 could not show which INT8 recipe produced results/runs/*int8 (README/run_sweep.sh say
on-the-fly FP8 on the base model; the manuscript says pre-quantized GPTQ-Int8 / w8a8;
the run JSON 'model' field is only the --model label). This captures four independent
records for each re-measured cell:
  1. vLLM's own startup log lines about quantization / dtype / weight loading
  2. the HF snapshot revision and its config.json 'quantization_config' (what the weights are)
  3. /v1/models as served
  4. GPU memory used and package versions
and ties them to the sha256 of every result file produced in the same serving session.

Usage: python capture_serving_recipe.py --served <s> --quant <q> --hf-id <id> --flags "<vllm flags>" \
          --server-log logs/serve_<s>_<q>.log --results <file> [<file> ...]
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, re, subprocess, time, urllib.request
from pathlib import Path


def sh(c):
    try: return subprocess.check_output(c, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e: return f"ERR:{e}"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--served", required=True); ap.add_argument("--quant", required=True)
    ap.add_argument("--hf-id", required=True); ap.add_argument("--flags", default="")
    ap.add_argument("--server-log", required=True); ap.add_argument("--results", nargs="*", default=[])
    ap.add_argument("--out-dir", default="results/v28_recipe")
    a = ap.parse_args()
    hf_home = os.environ.get("HF_HOME", "/workspace/hf-cache")
    snaps = sorted(glob.glob(f"{hf_home}/hub/models--{a.hf_id.replace('/', '--')}/snapshots/*"), key=os.path.getmtime)
    snap = snaps[-1] if snaps else None
    qcfg, torch_dtype = None, None
    if snap and os.path.isfile(f"{snap}/config.json"):
        cfg = json.load(open(f"{snap}/config.json"))
        qcfg, torch_dtype = cfg.get("quantization_config"), cfg.get("torch_dtype")
    log = Path(a.server_log).read_text(errors="replace") if os.path.isfile(a.server_log) else ""
    pat = re.compile(r"quantiz|gptq|marlin|awq|fp8|compressed|w8a8|dtype|Loading model weights|model weights took|Initializing an LLM engine", re.I)
    log_lines = [l.strip() for l in log.splitlines() if pat.search(l)][:60]
    try:
        models = json.load(urllib.request.urlopen(os.environ.get("OPENAI_BASE_URL", "http://localhost:8000/v1") + "/models", timeout=10))
    except Exception as e:
        models = {"error": str(e)}
    rec = {
        "cell": f"{a.served}_{a.quant}", "captured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hf_id": a.hf_id, "vllm_flags": a.flags,
        "hf_snapshot_revision": os.path.basename(snap) if snap else None,
        "weights_quantization_config": qcfg, "weights_torch_dtype": torch_dtype,
        "vllm_log_quantization_lines": log_lines, "served_models": models,
        "gpu": sh("nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader"),
        "versions": {p: sh(f"python -c 'import importlib.metadata as m;print(m.version(\"{p}\"))'") for p in ["vllm", "torch", "transformers"]},
        "results": [{"path": p, "sha256": sha(p)} for p in a.results if os.path.isfile(p)],
        "verdict_hint": ("pre-quantized checkpoint: " + str((qcfg or {}).get("quant_method"))) if qcfg
                        else ("on-the-fly flag: " + a.flags if "quantization" in a.flags else "NO quantization (full precision)"),
    }
    Path(a.out_dir).mkdir(parents=True, exist_ok=True)
    out = Path(a.out_dir) / f"{a.served}_{a.quant}.json"
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}\n  {rec['verdict_hint']}\n  log lines: {len(log_lines)}")
    if a.quant in ("int8", "int4") and not qcfg and "quantization" not in a.flags:
        print("!! WARNING: quantized cell but neither a quantization_config nor a --quantization flag was found")


if __name__ == "__main__":
    main()
