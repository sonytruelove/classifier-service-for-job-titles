from dataclasses import dataclass

from rapidfuzz import fuzz, process

from normalize import normalize

NO_MATCH_CODE = 'НЕТ СООТВЕТСТВИЯ'

MATCH_THRESHOLD = 0.78
REVIEW_HIGH = 0.90
# Ниже этого лучшего совпадения решение "нет соответствия" принимается уверенно
# и на ручную проверку не отправляется.
NO_MATCH_REVIEW_FLOOR = 0.60


@dataclass(frozen=True)
class ClassifierEntry:
    code: str
    name: str
    normalized_name: str


@dataclass(frozen=True)
class MatchResult:
    code: str
    name: str
    confidence: float
    needs_review: bool


def build_classifier_index(entries: list[tuple[str, str]]) -> list[ClassifierEntry]:
    return [ClassifierEntry(code, name, normalize(name)) for code, name in entries]


def match_position(raw_name: str, classifier: list[ClassifierEntry]) -> MatchResult:
    query = normalize(raw_name)

    if not query:
        return MatchResult(NO_MATCH_CODE, '', 1.0, False)

    choices = {entry.normalized_name: entry for entry in classifier}
    best = process.extractOne(query, choices.keys(), scorer=fuzz.token_sort_ratio)

    if best is None:
        return MatchResult(NO_MATCH_CODE, '', 1.0, False)

    matched_norm, score, _ = best
    confidence = round(score / 100, 4)
    entry = choices[matched_norm]

    if confidence >= MATCH_THRESHOLD:
        needs_review = confidence < REVIEW_HIGH
        return MatchResult(entry.code, entry.name, confidence, needs_review)

    no_match_confidence = round(1 - confidence, 4)
    needs_review = confidence >= NO_MATCH_REVIEW_FLOOR
    return MatchResult(NO_MATCH_CODE, '', no_match_confidence, needs_review)
