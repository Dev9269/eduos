"""Tests for Server/similarity.py tokenizer robustness."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Server.similarity import tokenize_code, similarity_score


def test_url_string_is_not_truncated_by_comment_strip():
    """A URL string must survive tokenization intact."""
    toks = tokenize_code('url = "https://example.com/path"\nprint(url)')
    assert 'STR' in toks
    assert '"https:' not in toks


def test_hash_inside_string_is_not_treated_as_comment():
    """A '# ' inside a string literal is data, not a comment."""
    toks = tokenize_code('msg = "hello # not a comment"\nprint(msg)')
    assert 'STR' in toks
    assert len(toks) == 4  # msg / = / STR / print(msg)


def test_slash_slash_inside_string_is_not_truncated():
    toks = tokenize_code("s = '// not a comment'\nprint(s)")
    assert 'STR' in toks
    assert "'//" not in toks


def test_real_comment_is_still_stripped():
    toks = tokenize_code('x = 1  # actual comment\nprint(x)')
    assert 'comment' not in toks
    assert toks == ['x', '=', 'NUM', 'print(x)']


def test_triple_quoted_multiline_string_protected():
    toks = tokenize_code('d = """multi\nline # keep"""\nprint(d)')
    assert 'STR' in toks


def test_similarity_still_detects_near_identical_with_urls():
    """Near-identical code that differs only in a URL must still flag high."""
    a = 'import requests\nr = requests.get("https://api.x.com")\nprint(r)'
    b = 'import requests\nr = requests.get("https://api.x.org")\nprint(r)'
    assert similarity_score(a, b) >= 0.7
