import math

from scripts.eval import _ndcg_at_k, precision_at_k, recovery_at_k


def test_precision_at_k():
    ranked = ["A", "B", "C", "D", "E"]
    ideal = ["A", "C", "X"]
    assert precision_at_k(ranked, ideal, k=5) == 0.4
    assert precision_at_k(ranked, ideal, k=10) == 0.2


def test_recovery_at_k():
    ranked = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    ideal = ["A", "C", "X", "Y"]
    found, total = recovery_at_k(ranked, ideal, k=10)
    assert found == 2
    assert total == 4


def test_ndcg_at_k_perfect():
    ideal = ["A", "B", "C"]
    ranked = ["A", "B", "C", "D"]
    assert math.isclose(_ndcg_at_k(ranked, ideal, k=3), 1.0)
