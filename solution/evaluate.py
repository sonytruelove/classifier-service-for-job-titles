import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from io_utils import read_classifier, read_labeled_sample
from match import NO_MATCH_CODE, build_classifier_index, match_position


def main() -> None:
    classifier = build_classifier_index(read_classifier())
    labeled = read_labeled_sample()

    correct = 0
    correct_high_conf = 0
    total_high_conf = 0
    mismatches = []

    for record_id, raw_name, true_code, true_name in labeled:
        result = match_position(raw_name, classifier)
        is_correct = result.code == true_code
        if is_correct:
            correct += 1
        else:
            mismatches.append((record_id, raw_name, true_code, result.code, result.confidence))

        if not result.needs_review:
            total_high_conf += 1
            if is_correct:
                correct_high_conf += 1

    total = len(labeled)
    accuracy = correct / total
    print(f'Accuracy на labeled_sample.csv: {correct}/{total} = {accuracy:.2%}')

    if total_high_conf:
        hc_accuracy = correct_high_conf / total_high_conf
        print(
            f'Accuracy среди записей без пометки "требует проверки": '
            f'{correct_high_conf}/{total_high_conf} = {hc_accuracy:.2%}'
        )
    else:
        print('Все записи помечены как "требует проверки"')

    no_match_true = [r for r in labeled if r[2] == NO_MATCH_CODE]
    no_match_correct = sum(
        1 for r in no_match_true
        if match_position(r[1], classifier).code == NO_MATCH_CODE
    )
    print(
        f'НЕТ СООТВЕТСТВИЯ распознано верно: '
        f'{no_match_correct}/{len(no_match_true)}'
    )

    if mismatches:
        print('\nРасхождения с эталоном:')
        for record_id, raw_name, true_code, got_code, conf in mismatches:
            print(f'  id={record_id} "{raw_name}" ожидалось={true_code} получено={got_code} (уверенность={conf:.2f})')


if __name__ == '__main__':
    main()
