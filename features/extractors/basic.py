from ..base import FeatureExtractor

import re
import numpy as np

class BasicFeatureExtractor(FeatureExtractor):
    def extract_features(self, code: str):
        lines = code.split("\n")
        line_lengths = [len(l) for l in lines if l.strip()]

        features = {
            "n_lines": len(lines),
            "avg_line_len": np.mean(line_lengths) if line_lengths else 0.0,
            "n_chars": len(code),
            "n_tabs": code.count("\t"),
            "n_spaces": code.count(" "),
            "n_keywords": len(re.findall(r"\b(for|while|if|class|def|return|function|var|let|const)\b", code)),
        }

        return features


