# A-09 길이대응 placebo — MEagent_trap(n=12, D1·D2·D4·D6) 3-조건 비교

| 조건 | MEagent_trap 평균 [범위] |
|------|--------------------------|
| concealed (은폐) | 80.1 [66.7, 100.0]  (n_cfg=13) |
| disclosed (공개) | 64.1 [41.7, 91.7]  (n_cfg=13) |
| placebo  (위약) | 78.8 [66.7, 100.0]  (n_cfg=13) |

## 판정 (Appendix B.4)
- placebo ≈ concealed → 조건 효과는 **드러난 정보** 때문. 5.2절 대비 유지(교란 아님).
- placebo ≈ disclosed → 대비가 **주석의 존재 자체**와 교란됨. 재해석 필요.

## 검증 노트
placebo 실행 전에는 concealed/disclosed 두 열만 채워지며, 그 평균이 원고의
concealed≈80.1%·disclosed≈64.1%와 일치해야 집계 로직이 옳다.

## 산출물
- results/a19/placebo_compare.csv, a09_placebo.json