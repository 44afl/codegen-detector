from __future__ import annotations
from typing import Dict, Any
from ..base import FeatureExtractor

class ASTStatsExtractor(FeatureExtractor):
    """Ex: nr. noduri/funcții/clase din AST-ul Python (fallback dacă nu e python)."""
    def extract_features(self, code: str, lang: str | None = None) -> Dict[str, Any]:
        if (lang or "").lower() != "python":
            return {"ast_nodes": 0, "ast_funcs": 0, "ast_classes": 0}
        import ast
        try:
            tree = ast.parse(code)
        except Exception:
            return {"ast_nodes": 0, "ast_funcs": 0, "ast_classes": 0}
        nodes = list(ast.walk(tree))
        funcs = sum(1 for n in nodes if isinstance(n, ast.FunctionDef))
        classes = sum(1 for n in nodes if isinstance(n, ast.ClassDef))
        return {"ast_nodes": len(nodes), "ast_funcs": funcs, "ast_classes": classes}
