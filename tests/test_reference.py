"""Regression test: corpus + instrument reproduce paper Tables 3-4 exactly."""
from overpriv.corpus_gen import build_corpus
from overpriv.sandbox import execute
from overpriv.policies import REFERENCE_POLICIES
from overpriv.metrics import score

TASKS = build_corpus()


def _pp(name):
    ms = [execute(t, REFERENCE_POLICIES[name](t)) for t in TASKS]
    return score(ms, TASKS).pp()


def test_corpus_shape():
    assert len(TASKS) == 198
    from collections import Counter
    assert Counter(t["label"] for t in TASKS) == {
        "normal": 90, "legit_high": 36, "attack": 72}
    assert Counter(t["gold_tier"] for t in TASKS) == {1: 54, 2: 75, 3: 33, 4: 18, 5: 18}


def test_table3():
    exp = {
        "P_gold": (0.0, 18.2, -18.2, 0.0),
        "P_greedy": (90.9, 72.7, 18.2, 63.6),
        "P_naive": (90.9, 100.0, -9.1, 90.9),
        "P_confused": (36.4, 53.0, -16.7, 34.8),
    }
    for name, (ei, eim, eg, ed) in exp.items():
        v = _pp(name)
        assert abs(v["intent_over_privilege_rate"] - ei) <= 0.15, name
        assert abs(v["impact_escalation_rate"] - eim) <= 0.15, name
        assert abs(v["iii_gap_pp"] - eg) <= 0.15, name
        assert abs(v["dual_confirmed_rate"] - ed) <= 0.15, name


def test_avg_delta_tier():
    assert abs(_pp("P_greedy")["avg_delta_tier_overpriv"] - 1.90) <= 0.02
    assert abs(_pp("P_confused")["avg_delta_tier_overpriv"] - 2.46) <= 0.02
    assert abs(_pp("P_naive")["avg_delta_tier_overpriv"] - 2.92) <= 0.02


def test_table4_decomposition():
    v = _pp("P_confused")
    assert abs(v["both_violate"] - 34.8) <= 0.15
    assert abs(v["harmless_over"] - 1.5) <= 0.15
    assert abs(v["missed_escalation"] - 18.2) <= 0.15
    assert abs(v["clean"] - 45.5) <= 0.15
