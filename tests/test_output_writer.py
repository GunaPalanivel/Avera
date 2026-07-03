import csv
from pathlib import Path

import pytest
from src.exceptions import OutputError
from src.models import CandidateModel
from src.output_writer import validate_output_canary, write_submission
from tests.test_scorers import get_base_candidate


def test_write_submission(tmp_path: Path):
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)

    results = [(0.950, 0.72, c, "Strong AI Engineer at Product Corp Join probability: 72%.")]

    out_file = tmp_path / "submission.csv"
    write_submission(out_file, results, input_ids={c.candidate_id}, expected_rows=1)

    assert out_file.exists()

    with out_file.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["candidate_id", "rank", "score", "reasoning"]

        row1 = next(reader)
        assert row1[0] == c.candidate_id
        assert row1[1] == "1"
        assert row1[2] == "0.9500"
        assert row1[3] == "Strong AI Engineer at Product Corp Join probability: 72%."


def test_write_submission_xlsx_has_join_probability(tmp_path: Path):
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)
    results = [(0.950, 0.6800, c, "reason")]
    out_file = tmp_path / "submission.csv"
    write_submission(out_file, results, input_ids={c.candidate_id}, expected_rows=1)
    import openpyxl

    wb = openpyxl.load_workbook(tmp_path / "submission.xlsx")
    assert wb.active.max_column == 5
    assert [cell.value for cell in wb.active[1]] == [
        "candidate_id",
        "rank",
        "score",
        "join_probability",
        "reasoning",
    ]


def test_canary_rejects_duplicate_ids():
    c = CandidateModel.model_validate(get_base_candidate())
    results = [(0.9, 0.5, c, "a"), (0.8, 0.5, c, "b")]
    with pytest.raises(OutputError, match="duplicate"):
        validate_output_canary(results, expected_rows=2)


def test_canary_rejects_id_not_in_input_pool():
    c = CandidateModel.model_validate(get_base_candidate())
    results = [(0.9, 0.5, c, "a")]
    with pytest.raises(OutputError, match="not in input"):
        validate_output_canary(results, input_ids=set(), expected_rows=1)
