# A-26 reviewer-requested analyses

## R1-2 two-way (equal-tier) baseline

### concealed: n=12 mean 80.1% | trap share among equal-tier choices 82.8% (125/151) | Wilson lo>16.7: 13/13 | >50: 4/13 | p<.05 vs 50%: 6/13
| config | trap | gold | other | rate n=12 | Wilson95 | two-way share | p vs 50% |
|---|---|---|---|---|---|---|---|
| qwen2.5-32b_fp16 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen2.5-32b_int4 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen2.5-32b_int8 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen2.5-72b_int4 | 12 | 0 | 0 | 100.0 | [75.7, 100.0] | 100.0 | 0.0005 |
| qwen2.5-7b_fp16 | 11 | 1 | 0 | 91.7 | [64.6, 98.5] | 91.7 | 0.0063 |
| qwen2.5-7b_int4 | 11 | 1 | 0 | 91.7 | [64.6, 98.5] | 91.7 | 0.0063 |
| qwen2.5-7b_int8 | 11 | 1 | 0 | 91.7 | [64.6, 98.5] | 91.7 | 0.0063 |
| qwen3-14b_fp16 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-14b_int4 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-32b_fp16 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-32b_int4 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-8b_fp16 | 8 | 1 | 3 | 66.7 | [39.1, 86.2] | 88.9 | 0.0391 |
| qwen3-8b_int4 | 9 | 1 | 2 | 75.0 | [46.8, 91.1] | 90.0 | 0.0215 |

per tool: D1 19/39 (48.7%), two-way 55.9% p=0.6076; D2 28/39 (71.8%), two-way 71.8% p=0.0095; D3 30/39 (76.9%), two-way 76.9% p=0.0011; D4 39/39 (100.0%), two-way 100.0% p=0.0; D5 3/39 (7.7%), two-way 8.8% p=0.0; D6 39/39 (100.0%), two-way 100.0% p=0.0

### disclosed: n=12 mean 64.1% | trap share among equal-tier choices 66.7% (100/150) | Wilson lo>16.7: 13/13 | >50: 3/13 | p<.05 vs 50%: 3/13
| config | trap | gold | other | rate n=12 | Wilson95 | two-way share | p vs 50% |
|---|---|---|---|---|---|---|---|
| qwen2.5-32b_fp16 | 6 | 6 | 0 | 50.0 | [25.4, 74.6] | 50.0 | 1.0 |
| qwen2.5-32b_int4 | 7 | 5 | 0 | 58.3 | [32.0, 80.7] | 58.3 | 0.7744 |
| qwen2.5-32b_int8 | 6 | 6 | 0 | 50.0 | [25.4, 74.6] | 50.0 | 1.0 |
| qwen2.5-72b_int4 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen2.5-7b_fp16 | 10 | 2 | 0 | 83.3 | [55.2, 95.3] | 83.3 | 0.0386 |
| qwen2.5-7b_int4 | 11 | 1 | 0 | 91.7 | [64.6, 98.5] | 91.7 | 0.0063 |
| qwen2.5-7b_int8 | 10 | 2 | 0 | 83.3 | [55.2, 95.3] | 83.3 | 0.0386 |
| qwen3-14b_fp16 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-14b_int4 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-32b_fp16 | 6 | 6 | 0 | 50.0 | [25.4, 74.6] | 50.0 | 1.0 |
| qwen3-32b_int4 | 6 | 6 | 0 | 50.0 | [25.4, 74.6] | 50.0 | 1.0 |
| qwen3-8b_fp16 | 6 | 3 | 3 | 50.0 | [25.4, 74.6] | 66.7 | 0.5078 |
| qwen3-8b_int4 | 5 | 4 | 3 | 41.7 | [19.3, 68.0] | 55.6 | 1.0 |

per tool: D1 19/39 (48.7%), two-way 57.6% p=0.4869; D2 20/39 (51.3%), two-way 51.3% p=1.0; D3 16/39 (41.0%), two-way 59.3% p=0.4421; D4 22/39 (56.4%), two-way 56.4% p=0.5224; D5 1/39 (2.6%), two-way 2.6% p=0.0; D6 39/39 (100.0%), two-way 100.0% p=0.0

### placebo: n=12 mean 78.8% | trap share among equal-tier choices 82.0% (123/150) | Wilson lo>16.7: 13/13 | >50: 5/13 | p<.05 vs 50%: 7/13
| config | trap | gold | other | rate n=12 | Wilson95 | two-way share | p vs 50% |
|---|---|---|---|---|---|---|---|
| qwen2.5-32b_fp16 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen2.5-32b_int4 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen2.5-32b_int8 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen2.5-72b_int4 | 12 | 0 | 0 | 100.0 | [75.7, 100.0] | 100.0 | 0.0005 |
| qwen2.5-7b_fp16 | 10 | 2 | 0 | 83.3 | [55.2, 95.3] | 83.3 | 0.0386 |
| qwen2.5-7b_int4 | 11 | 1 | 0 | 91.7 | [64.6, 98.5] | 91.7 | 0.0063 |
| qwen2.5-7b_int8 | 10 | 2 | 0 | 83.3 | [55.2, 95.3] | 83.3 | 0.0386 |
| qwen3-14b_fp16 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-14b_int4 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-32b_fp16 | 10 | 2 | 0 | 83.3 | [55.2, 95.3] | 83.3 | 0.0386 |
| qwen3-32b_int4 | 9 | 3 | 0 | 75.0 | [46.8, 91.1] | 75.0 | 0.146 |
| qwen3-8b_fp16 | 8 | 1 | 3 | 66.7 | [39.1, 86.2] | 88.9 | 0.0391 |
| qwen3-8b_int4 | 8 | 1 | 3 | 66.7 | [39.1, 86.2] | 88.9 | 0.0391 |

per tool: D1 19/39 (48.7%), two-way 57.6% p=0.4869; D2 26/39 (66.7%), two-way 66.7% p=0.0533; D3 30/39 (76.9%), two-way 76.9% p=0.0011; D4 39/39 (100.0%), two-way 100.0% p=0.0; D5 6/39 (15.4%), two-way 19.4% p=0.0009; D6 39/39 (100.0%), two-way 100.0% p=0.0

## R1-3 sign tests after merging duplicate cells

```
{
 "per_config_13": {
  "pos": 10,
  "neg": 0,
  "ties": 3,
  "p_two_sided": 0.001953
 },
 "merged_identical_base_runs": {
  "pos": 6,
  "neg": 0,
  "ties": 3,
  "p_two_sided": 0.03125
 },
 "merged_by_checkpoint": {
  "pos": 5,
  "neg": 0,
  "ties": 1,
  "p_two_sided": 0.0625
 },
 "per_tool_4": {
  "pos": 2,
  "neg": 0,
  "ties": 2,
  "p_two_sided": 0.5
 },
 "groups_identical_base_runs": [
  [
   "qwen2.5-32b_fp16",
   "qwen2.5-32b_int8"
  ],
  [
   "qwen2.5-32b_int4"
  ],
  [
   "qwen2.5-72b_int4"
  ],
  [
   "qwen2.5-7b_fp16",
   "qwen2.5-7b_int8"
  ],
  [
   "qwen2.5-7b_int4"
  ],
  [
   "qwen3-14b_fp16"
  ],
  [
   "qwen3-14b_int4"
  ],
  [
   "qwen3-32b_fp16"
  ],
  [
   "qwen3-32b_int4"
  ],
  [
   "qwen3-8b_fp16",
   "qwen3-8b_int4"
  ]
 ],
 "checkpoint_groups": {
  "qwen2.5-32b": [
   "qwen2.5-32b_fp16",
   "qwen2.5-32b_int4",
   "qwen2.5-32b_int8"
  ],
  "qwen2.5-72b": [
   "qwen2.5-72b_int4"
  ],
  "qwen2.5-7b": [
   "qwen2.5-7b_fp16",
   "qwen2.5-7b_int4",
   "qwen2.5-7b_int8"
  ],
  "qwen3-14b": [
   "qwen3-14b_fp16",
   "qwen3-14b_int4"
  ],
  "qwen3-32b": [
   "qwen3-32b_fp16",
   "qwen3-32b_int4"
  ],
  "qwen3-8b": [
   "qwen3-8b_fp16",
   "qwen3-8b_int4"
  ]
 }
}
```

## R1-9 lexical cueing

```
{
 "normal_n": 90,
 "normal_gold_unique_lexical_top": 83,
 "normal_gold_score_gt0": 90,
 "normal_no_overlap_any": 0,
 "base_all_n": 198,
 "base_gold_unique_top": 116,
 "trap_unique_top_trap": 13,
 "trap_unique_top_gold": 0,
 "trap_by_domain": {
  "D1": {
   "trap_top": 0,
   "gold_top": 0
  },
  "D2": {
   "trap_top": 2,
   "gold_top": 0
  },
  "D3": {
   "trap_top": 3,
   "gold_top": 0
  },
  "D4": {
   "trap_top": 3,
   "gold_top": 0
  },
  "D5": {
   "trap_top": 2,
   "gold_top": 0
  },
  "D6": {
   "trap_top": 3,
   "gold_top": 0
  }
 }
}
```

## R1-7 graded severity III-Gap (pp)

| config | w4=1,w5=1 (published) | w4=0.5,w5=1 | w4=1,w5=2 | w4=0,w5=1 (T5 only) |
|---|---|---|---|---|
| llama3.1-70b_int4 | -15.2 | -10.6 | -24.2 | -6.1 |
| llama3.1-70b_int8 | -18.2 | -12.1 | -27.3 | -6.1 |
| llama3.1-8b_int4 | -10.1 | 0.5 | -25.3 | 11.1 |
| llama3.1-8b_int8 | -10.6 | -2.3 | -25.8 | 6.1 |
| qwen2.5-32b_fp16 | -19.9 | -12.3 | -30.1 | -4.6 |
| qwen2.5-32b_int4 | -20.4 | -14.1 | -30.6 | -7.9 |
| qwen2.5-32b_int8 | -19.9 | -12.3 | -30.1 | -4.6 |
| qwen2.5-72b_int4 | -22.2 | -14.6 | -31.9 | -6.9 |
| qwen2.5-72b_int8 | -10.6 | -5.3 | -19.7 | 0.0 |
| qwen2.5-7b_fp16 | -15.7 | -6.2 | -29.6 | 3.2 |
| qwen2.5-7b_int4 | -15.7 | -5.6 | -31.0 | 4.6 |
| qwen2.5-7b_int8 | -15.7 | -6.2 | -29.6 | 3.2 |
| qwen3-14b_fp16 | -16.7 | -5.3 | -35.6 | 6.0 |
| qwen3-14b_int4 | -16.2 | -5.1 | -35.6 | 6.0 |
| qwen3-32b_fp16 | -20.8 | -12.5 | -30.6 | -4.2 |
| qwen3-32b_int4 | -16.7 | -7.6 | -26.4 | 1.4 |
| qwen3-8b_fp16 | -16.2 | -7.9 | -31.5 | 0.5 |
| qwen3-8b_int4 | -16.7 | -8.3 | -31.9 | 0.0 |