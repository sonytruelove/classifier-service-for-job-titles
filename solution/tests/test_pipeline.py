import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from io_utils import read_classifier, read_labeled_sample, read_raw_positions
import evaluate
import run


def test_io_utils_read_expected_row_counts():
    assert len(read_classifier()) == 56
    assert len(read_raw_positions()) == 300
    assert len(read_labeled_sample()) == 50


def test_run_main_writes_results_csv_for_every_raw_position():
    run.main()
    with open(run.OUTPUT_PATH, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f, delimiter=';'))
    assert rows[0] == [
        'id', 'исходное наименование', 'код', 'наименование по классификатору',
        'уверенность', 'требует проверки',
    ]
    assert len(rows) - 1 == 300
    assert all(row[5] in ('да', 'нет') for row in rows[1:])


def test_evaluate_main_runs_without_error(capsys):
    evaluate.main()
    out = capsys.readouterr().out
    assert 'Accuracy на labeled_sample.csv' in out
