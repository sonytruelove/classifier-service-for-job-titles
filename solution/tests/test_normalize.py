import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from normalize import normalize


def test_lowercases_and_strips_extra_spaces():
    assert normalize('  ПЛОТНИК  ') == 'плотник'


def test_removes_grade_suffix():
    assert normalize('Плотник 5 разряда') == 'плотник'
    assert normalize('Инженер-геодезист 1 категории') == 'инженер-геодезист'


def test_removes_employment_type_suffix():
    assert normalize('Каменщик (вахта)') == 'каменщик'
    assert normalize('Токарь (совм.)') == 'токарь'
    assert normalize('Плотник (осн.)') == 'плотник'


def test_removes_organization_mention():
    assert normalize('Нач. участка АО "МостСтрой"') == 'начальник участка'
    assert normalize('Газорезчик ООО "СтройМонтаж"') == 'газорезчик'


def test_expands_known_abbreviations():
    assert normalize('Маш. катка') == 'машинист катка'
    assert normalize('Бурильщик руч. бурения') == 'бурильщик ручного бурения'
    assert normalize('Инженер ПТО') == 'инженер производственно-технического отдела'


def test_operator_avtokrana_maps_to_mashinist_krana():
    assert normalize('ОПЕРАТОР АВТОКРАНА') == 'машинист крана автомобильного'
    assert normalize('крановщик автокрана') == 'машинист крана автомобильного'
    assert normalize('Машинист автокрана') == 'машинист крана автомобильного'


def test_shofer_is_synonym_for_voditel():
    assert normalize('ШОФЕР САМОСВАЛА') == 'водитель самосвала'


def test_buldozerist_maps_to_mashinist_buldozera():
    assert normalize('Бульдозерист 3 разряда') == 'машинист бульдозера'


def test_role_word_typo_still_triggers_synonym():
    # "операттор" — опечатка (лишняя "т"), но должна распознаваться как "оператор"
    assert normalize('операттор экскаватора') == 'машинист экскаватора'


def test_empty_string_stays_empty():
    assert normalize('') == ''
    assert normalize('   ') == ''
