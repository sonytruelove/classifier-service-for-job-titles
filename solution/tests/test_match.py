import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from io_utils import read_classifier
from match import NO_MATCH_CODE, build_classifier_index, match_position

CLASSIFIER = build_classifier_index(read_classifier())


def test_exact_name_matches_with_high_confidence():
    result = match_position('Каменщик', CLASSIFIER)
    assert result.code == 'КЛС-005'
    assert result.confidence >= 0.90
    assert result.needs_review is False


def test_typo_still_resolves_to_correct_code():
    result = match_position('Каенщик', CLASSIFIER)
    assert result.code == 'КЛС-005'


def test_synonym_operator_avtokrana_resolves_to_mashinist_krana():
    result = match_position('ОПЕРАТОР АВТОКРАНА', CLASSIFIER)
    assert result.code == 'КЛС-025'
    assert result.name == 'Машинист крана автомобильного'


def test_office_position_returns_no_match():
    result = match_position('Повар столовой', CLASSIFIER)
    assert result.code == NO_MATCH_CODE
    assert result.name == ''


def test_unrelated_office_position_is_not_flagged_for_review():
    # Достаточно далеко от любой должности классификатора — можно не проверять руками.
    result = match_position('Юрисконсульт', CLASSIFIER)
    assert result.code == NO_MATCH_CODE
    assert result.needs_review is False


def test_ambiguous_case_is_not_confidently_assigned_a_wrong_code():
    # "Специалист по сметам" не входит в эталон. По буквам он не совпадает ни
    # с одной строкой классификатора настолько, чтобы претендовать на код —
    # система не должна молча приписывать ему конкретный код классификатора.
    # Известное ограничение: т.к. по написанию это так же далеко от "Сметчика",
    # как и типичные нерелевантные офисные должности, отдельно на проверку
    # это не попадает — см. README, раздел "known limitations".
    result = match_position('Специалист по сметам', CLASSIFIER)
    assert result.code == NO_MATCH_CODE


def test_prorab_clarified_in_parens_resolves_to_prorab():
    result = match_position('Прораб (производитель работ)', CLASSIFIER)
    assert result.code == 'КЛС-046'
    assert result.confidence >= 0.90


def test_buldozerist_resolves_to_mashinist_buldozera():
    result = match_position('БУЛЬДОЗЕРИСТ 6 РАЗРЯДА', CLASSIFIER)
    assert result.code == 'КЛС-029'


def test_grade_and_org_suffix_do_not_affect_match():
    a = match_position('Плотник', CLASSIFIER)
    b = match_position('Плотник 5 разряда', CLASSIFIER)
    c = match_position('Плотник ООО "СтройМонтаж"', CLASSIFIER)
    assert a.code == b.code == c.code == 'КЛС-006'
