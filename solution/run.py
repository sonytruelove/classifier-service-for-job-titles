import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from io_utils import read_classifier, read_raw_positions
from match import build_classifier_index, match_position

OUTPUT_PATH = Path(__file__).resolve().parent.parent / 'results.csv'


def main() -> None:
    classifier = build_classifier_index(read_classifier())
    raw_positions = read_raw_positions()

    with open(OUTPUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            'id', 'исходное наименование', 'код', 'наименование по классификатору',
            'уверенность', 'требует проверки',
        ])
        for record_id, raw_name in raw_positions:
            result = match_position(raw_name, classifier)
            writer.writerow([
                record_id,
                raw_name,
                result.code,
                result.name,
                f'{result.confidence:.2f}',
                'да' if result.needs_review else 'нет',
            ])

    print(f'Готово: {len(raw_positions)} записей сохранено в {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
