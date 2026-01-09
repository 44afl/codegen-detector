import pytest

from features.decorator import (
    CommentRemovalDecorator,
    IndentationStyleDecorator,
    IdentifierEntropyDecorator,
    PerplexityLikeDecorator,
)


class DummyExtractor:
    def __init__(self):
        self.last_code = None
        self.last_lang = None

    def extract_features(self, code: str, lang=None):
        self.last_code = code
        self.last_lang = lang
        return {"base": 1}


class BasicFeatureExtractorCompat:
    def extract_features(self, code: str, lang=None):
        lines = code.splitlines()
        if not lines:
            avg = 0.0
        else:
            avg = sum(len(l) for l in lines) / len(lines)
        return {"avg_line_len": avg}


def test_comment_removal_python_hash():
    base = DummyExtractor()
    dec = CommentRemovalDecorator(base)

    code = "x = 1  # comment\nprint(x)\n"
    feats = dec.extract_features(code, lang="python")
    assert base.last_code.splitlines()[0].rstrip() == "x = 1"
    assert feats["comments_removed"] is True
    assert feats["base"] == 1
    


def test_comment_removal_default_slashes():
    base = DummyExtractor()
    dec = CommentRemovalDecorator(base)

    code = "int a = 0; // comment\nreturn a;\n"
    feats = dec.extract_features(code, lang=None)

    # comentariul cu // trebuie eliminat
    assert base.last_code.splitlines()[0].rstrip() == "int a = 0;"
    assert feats["comments_removed"] is True
    assert feats["base"] == 1


def test_indentation_style_counts():
    base = DummyExtractor()
    dec = IndentationStyleDecorator(base)

    code = "\tline1\n    line2\n  line3\nline4\n"
    feats = dec.extract_features(code, lang=None)

    assert feats["indent_tabs"] == 1
    assert feats["indent_spaces"] == 2
    assert feats["indent_4"] == 1
    assert feats["indent_2"] == 2
    assert feats["base"] == 1


def test_identifier_entropy_no_identifiers_returns_zero():
    base = DummyExtractor()
    dec = IdentifierEntropyDecorator(base)

    code = "123 456 !!!\n"
    feats = dec.extract_features(code, lang=None)

    assert feats["id_entropy"] == 0.0
    assert feats["base"] == 1


def test_perplexity_like_is_inverse_to_length():
    base = DummyExtractor()
    dec = PerplexityLikeDecorator(base)

    code = "abcd"  # len = 4 → 1 + 100 / 4 = 26
    feats = dec.extract_features(code, lang=None)

    assert feats["ppl_like"] == pytest.approx(26.0, rel=1e-4)
    assert feats["base"] == 1


def test_comment_removal_affects_average_line_length():
    code = "x=1 # comment\nprint(x)"
    base = BasicFeatureExtractorCompat()
    dec = CommentRemovalDecorator(base)

    f_base = base.extract_features(code, lang="python")["avg_line_len"]
    f_dec = dec.extract_features(code, lang="python")["avg_line_len"]
    assert f_dec < f_base


"""
venv) admin@Mac codegen-detector % pytest tests/test_feature_decorator_2.py \
  --cov=features.decorator \
  --cov-report=term-missing

================================================================================ test session starts ================================================================================
platform darwin -- Python 3.13.7, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/admin/Documents/Facultate/FII/Tehnici avansate de ingineria programarii/codegen-detector
configfile: pyproject.toml
plugins: cov-7.0.0
collected 6 items                                                                                                                                                                   

tests/test_feature_decorator_2.py ......                                                                                                                                      [100%]

================================================================================== tests coverage ===================================================================================
_________________________________________________________________ coverage: platform darwin, python 3.13.7-final-0 __________________________________________________________________

Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
features/decorator.py      63      7    89%   16, 80-85
-----------------------------------------------------
TOTAL                      63      7    89%
================================================================================= 6 passed in 0.04s =================================================================================
(venv) admin@Mac codegen-detector % 

"""