import re

from rapidfuzz import fuzz

_ORG_SUFFIX = re.compile(
    r'\b(ао|ооо|зао|пао|ип)\.?\s*["\'][^"\']*["\']',
    re.IGNORECASE,
)
_PAREN_SUFFIX = re.compile(r'\((осн|совм|вахта)\.?\)', re.IGNORECASE)
_BARE_PARENS = re.compile(r'[()]')
_GRADE_SUFFIX = re.compile(
    r'\b\d+\s*(разряда|разряд|категории|категория)\b',
    re.IGNORECASE,
)
_QUOTES = re.compile(r'["\'«»]')
_MULTI_SPACE = re.compile(r'\s+')

ABBREVIATIONS = {
    'маш.': 'машинист',
    'маш': 'машинист',
    'нач.': 'начальник',
    'нач': 'начальник',
    'строит.': 'строительной',
    'мех.': 'механического',
    'руч.': 'ручного',
    'констр.': 'конструкций',
    'сантех.': 'санитарно-технических',
    'технолог.': 'технологических',
    'эгс': 'электрогазосварщик',
    'пто': 'производственно-технического отдела',
}

# Словарь профжаргона: слова, которые буквально не похожи на канонические
# наименования классификатора, но обозначают ту же должность.
WORD_SYNONYMS = {
    'шофер': 'водитель',
    'шофёр': 'водитель',
    'бульдозерист': 'машинист бульдозера',
    'автокрана': 'крана автомобильного',
    'автокран': 'крана автомобильного',
}

PHRASE_SYNONYMS = (
    ('оператор автокрана', 'машинист крана автомобильного'),
    ('крановщик автокрана', 'машинист крана автомобильного'),
    ('крановщик башенного крана', 'машинист башенного крана'),
    ('оператор экскаватора', 'машинист экскаватора'),
    ('шофер самосвала', 'водитель самосвала'),
    ('шофёр самосвала', 'водитель самосвала'),
    ('сварщик эгс', 'электрогазосварщик'),
    # "прораб" и "производитель работ" — официальный синоним, часто дают
    # рядом как уточнение: "Прораб (производитель работ)".
    ('производитель работ', 'прораб'),
)

# Опорные слова профессиональной роли: часто встречаются с опечатками,
# но именно от них зависит срабатывание PHRASE_SYNONYMS выше.
_ROLE_ANCHORS = ('оператор', 'крановщик', 'машинист', 'водитель', 'бульдозерист', 'производитель')
_ANCHOR_MATCH_RATIO = 87


def _correct_role_typos(tokens: list[str]) -> list[str]:
    corrected = []
    for token in tokens:
        if len(token) < 5:
            corrected.append(token)
            continue
        best_anchor, best_score = None, 0
        for anchor in _ROLE_ANCHORS:
            score = fuzz.ratio(token, anchor)
            if score > best_score:
                best_anchor, best_score = anchor, score
        corrected.append(best_anchor if best_score >= _ANCHOR_MATCH_RATIO else token)
    return corrected


def normalize(text: str) -> str:
    s = text.lower()
    s = _ORG_SUFFIX.sub(' ', s)
    s = _PAREN_SUFFIX.sub(' ', s)
    s = _GRADE_SUFFIX.sub(' ', s)
    s = _QUOTES.sub(' ', s)
    s = _BARE_PARENS.sub(' ', s)
    s = _MULTI_SPACE.sub(' ', s).strip()

    tokens = s.split(' ') if s else []
    tokens = _correct_role_typos(tokens)
    s = ' '.join(tokens)

    for phrase, replacement in PHRASE_SYNONYMS:
        s = s.replace(phrase, replacement)

    tokens = s.split(' ') if s else []
    tokens = [ABBREVIATIONS.get(t, t) for t in tokens]
    tokens = [WORD_SYNONYMS.get(t, t) for t in tokens]
    tokens = _dedup_adjacent(tokens)
    s = ' '.join(tokens)
    s = _MULTI_SPACE.sub(' ', s).strip()
    return s


def _dedup_adjacent(tokens: list[str]) -> list[str]:
    result = []
    for token in tokens:
        if not result or result[-1] != token:
            result.append(token)
    return result
