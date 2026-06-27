import csv
from pathlib import Path

from src.models import CandidateModel
from src.output_writer import write_submission
from tests.test_scorers import get_base_candidate


def test_write_submission(tmp_path: Path):
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)

    results = [(0.950, c, "Strong AI Engineer at Product Corp"), (0.850, c, "Good fit")]

    out_file = tmp_path / "submission.csv"
    write_submission(out_file, results)

    assert out_file.exists()

    with out_file.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["candidate_id", "rank", "score", "reasoning"]

        row1 = next(reader)
        assert row1[0] == c.candidate_id
        assert row1[1] == "1"
        assert row1[2] == "0.9500"
        assert row1[3] == "Strong AI Engineer at Product Corp"

        row2 = next(reader)
        assert row2[0] == c.candidate_id
        assert row2[1] == "2"
        assert row2[2] == "0.8500"
        assert row2[3] == "Good fit"
