import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'


def read_classifier(path: Path = None) -> list[tuple[str, str]]:
    path = path or DATA_DIR / 'classifier.csv'
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        return [(row[0], row[1]) for row in reader if row]


def read_raw_positions(path: Path = None) -> list[tuple[str, str]]:
    path = path or DATA_DIR / 'raw_positions.csv'
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        return [(row[0], row[1]) for row in reader if row]


def read_labeled_sample(path: Path = None) -> list[tuple[str, str, str, str]]:
    path = path or DATA_DIR / 'labeled_sample.csv'
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        return [(row[0], row[1], row[2], row[3]) for row in reader if row]
