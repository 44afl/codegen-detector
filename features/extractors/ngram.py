from __future__ import annotations
from typing import Dict, Any
from collections import Counter
from ..base import FeatureExtractor

class NgramStatsExtractor(FeatureExtractor):
    """Distribuții simple de caractere / bigrame (limbă-agnostic)."""
    def __init__(self, k: int = 2, top: int = 10) -> None:
        self.k = k; self.top = top

    def extract_features(self, code: str, lang: str | None = None) -> Dict[str, Any]:
        s = code.replace("\n"," ")
        grams = [s[i:i+self.k] for i in range(len(s)-self.k+1)]
        freq = Counter(grams).most_common(self.top)
        # aplatizăm ca f1_gram=cnt
        out = {}
        for i,(g,c) in enumerate(freq, start=1):
            out[f"ngram_{self.k}_{i}__{g}"] = c
        out[f"ngram_{self.k}_uniq"] = len(set(grams))
        return out
