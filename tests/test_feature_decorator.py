from features.extractors.basic import BasicFeatureExtractor
from features.extractors.ast_stats import ASTStatsExtractor
from features.decorator import (CommentRemovalDecorator, IndentationStyleDecorator,
                                IdentifierEntropyDecorator, PerplexityLikeDecorator)

def test_comment_removal_affects_length():
    code = "x=1 # comment\nprint(x)"
    base = BasicFeatureExtractor()
    dec = CommentRemovalDecorator(base)

    print("\n=== DEBUG: ORIGINAL CODE ===")
    print(code)

    cleaned = dec._pre(code, lang="python")
    print("\n=== DEBUG: AFTER COMMENT REMOVAL ===")
    print(cleaned)

    f_base = base.extract_features(code)["avg_line_len"]
    f_dec  = dec.extract_features(code, lang="python")["avg_line_len"]
    print("\n=== DEBUG: FEATURES WITH DECORATOR ===")
    print(dec.extract_features(code, lang="python"))


    print("\n=== DEBUG: FEATURES WITHOUT DECORATOR ===")
    print(base.extract_features(code))


    assert f_dec <= f_base and dec.extract_features(code)["comments_removed"] is True


def test_chain_adds_expected_keys_python():
    code = "def f():\n    x = 1\n    return x"
    chain = PerplexityLikeDecorator(
                IdentifierEntropyDecorator(
                    IndentationStyleDecorator(
                        ASTStatsExtractor())))
    feats = chain.extract_features(code, lang="python")
    for key in ("ast_nodes","ast_funcs","id_entropy","indent_4","ppl_like"):
        assert key in feats
