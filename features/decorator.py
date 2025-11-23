from __future__ import annotations
from typing import Dict, Any
from .base import FeatureExtractor
from aop.aspects import log_call, timeit, debug

class FeatureDecorator(FeatureExtractor):
    """Base: wraps an extractor and adds PRE/POST processing."""
    
    def __init__(self, extractor: FeatureExtractor) -> None:
        self._extractor = extractor

    def _pre(self, code: str, lang: str | None) -> str:
        return code

    def _post(self, feats: Dict[str, Any], code: str, lang: str | None) -> Dict[str, Any]:
        return feats


    @log_call   
    @timeit
    def extract_features(self, code: str, lang: str | None = None) -> Dict[str, Any]:
        # print("\n[DEBUG DECORATOR] ORIGINAL CODE:")
        # print(repr(code))
        code2 = self._pre(code, lang)
        # print("[DEBUG DECORATOR] AFTER _pre:")
        # print(repr(code2))
        base_feats = self._extractor.extract_features(code2, lang)
        # print("[DEBUG DECORATOR] BASE FEATS ON CLEANED CODE:")
        # print(base_feats)
        final = self._post(base_feats, code, lang)
        # print("[DEBUG DECORATOR] FINAL FEATS AFTER _post:")
        # print(final)
        return final

class CommentRemovalDecorator(FeatureDecorator):
    """PRE: removes single-line comments (# //) in common languages."""
    @debug
    def _pre(self, code: str, lang: str | None) -> str:
        out = []
        for ln in code.splitlines():
            if lang and lang.lower() in ("python","py"):
                out.append(ln.split("#", 1)[0])
            else:
                cut = ln.split("//", 1)[0]
                out.append(cut)
        return "\n".join(out)

    def _post(self, feats: Dict[str, Any], code: str, lang: str | None) -> Dict[str, Any]:
        d = dict(feats)
        d["comments_removed"] = True
        return d

class IndentationStyleDecorator(FeatureDecorator):
    """POST: analyzes indentation style in the code."""
    def _post(self, feats: Dict[str, Any], code: str, lang: str | None) -> Dict[str, Any]:
        d = dict(feats)
        lines = [l for l in code.splitlines() if l.strip()]
        tabs = sum(1 for l in lines if l.startswith("\t"))
        spaces = sum(1 for l in lines if l.startswith(" "))
        four = sum(1 for l in lines if l.startswith("    "))
        two = sum(1 for l in lines if l.startswith("  "))
        d.update({
            "indent_tabs": tabs,
            "indent_spaces": spaces,
            "indent_4": four,
            "indent_2": two,
        })
        return d

class IdentifierEntropyDecorator(FeatureDecorator):
    """POST: calculates entropy of identifiers in the code."""
    def _post(self, feats: Dict[str, Any], code: str, lang: str | None) -> Dict[str, Any]:
        import re, math
        from collections import Counter
        d = dict(feats)
        ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code)
        if not ids:
            d["id_entropy"] = 0.0
            return d
        joined = "".join(ids)
        cnt = Counter(joined)
        total = sum(cnt.values())
        H = -sum((c/total) * math.log2(c/total) for c in cnt.values())
        d["id_entropy"] = round(H, 4)
        return d

class PerplexityLikeDecorator(FeatureDecorator):
    """POST: adds a perplexity-like feature based on code length."""
    def _post(self, feats: Dict[str, Any], code: str, lang: str | None) -> Dict[str, Any]:
        d = dict(feats)
        L = max(1, len(code))
        d["ppl_like"] = round(1.0 + 100.0 / L, 4)
        return d
