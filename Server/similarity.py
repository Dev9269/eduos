"""
EduOS Code Similarity Checker
Simple token-based similarity detection for coding exam submissions.
Not a full MOSS implementation, but catches obvious copy-paste.
"""

import re
import json
from pathlib import Path
from itertools import combinations


def tokenize_code(code: str) -> list:
    """Strip comments, whitespace, variable names → token list"""
    # Remove single-line comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    # Remove strings
    code = re.sub(r'\".*?\"|\'.*?\'', 'STR', code)
    # Remove numbers
    code = re.sub(r'\b\d+\b', 'NUM', code)
    # Normalize whitespace
    tokens = re.split(r'\s+', code.strip())
    return [t for t in tokens if t]


def similarity_score(code_a: str, code_b: str) -> float:
    """
    Jaccard similarity on token n-grams.
    Returns 0.0 (no similarity) to 1.0 (identical).
    """
    if not code_a or not code_b:
        return 0.0

    def ngrams(tokens, n=3):
        return set(tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1))

    ta = tokenize_code(code_a)
    tb = tokenize_code(code_b)

    if len(ta) < 3 or len(tb) < 3:
        return 0.0

    nga = ngrams(ta)
    ngb = ngrams(tb)

    if not nga or not ngb:
        return 0.0

    intersection = len(nga & ngb)
    union = len(nga | ngb)
    return intersection / union if union > 0 else 0.0


def answers_to_code(answers) -> str:
    """Extract the code text from an answers dict.
    Prefers 'code', then common code keys (q2, answer, source, program),
    then the longest string value."""
    if not isinstance(answers, dict):
        return str(answers) if answers else ''
    if 'code' in answers:
        return str(answers['code'])
    for key in ('q2', 'answer', 'source', 'program'):
        if key in answers and answers[key]:
            return str(answers[key])
    vals = [str(v) for v in answers.values() if isinstance(v, str) and v]
    return max(vals, key=len) if vals else ''


def check_submissions_for_similarity(
    submissions: list,
    threshold: float = 0.7
) -> list:
    """
    Compare all pairs of submissions.
    Returns list of suspicious pairs above threshold.
    """
    suspicious = []
    for a, b in combinations(submissions, 2):
        a_code = answers_to_code(a.get('answers', {}))
        b_code = answers_to_code(b.get('answers', {}))
        if not a_code or not b_code:
            continue
        score = similarity_score(a_code, b_code)
        if score >= threshold:
            suspicious.append({
                'student_a': a.get('student_id'),
                'student_b': b.get('student_id'),
                'similarity': round(score, 3),
                'flag': 'HIGH' if score >= 0.9 else 'MEDIUM'
            })
    return sorted(suspicious, key=lambda x: x['similarity'], reverse=True)
