from __future__ import annotations
from typing import Dict, Any
from ..base import FeatureExtractor

class BasicFeatureExtractor(FeatureExtractor):
    """number of lines, average line length."""

    def extract_features(self, code: str, lang: str | None = None) -> Dict[str, Any]:
        # print("\n[DEBUG BASIC] CODE RECEIVED IN BasicFeatureExtractor:")
        # print(repr(code))
        lines = code.splitlines()
        n = len(lines)
        avg_len = (sum(len(l) for l in lines) / n) if n else 0.0
        return {"n_lines": n, "avg_line_len": avg_len}



