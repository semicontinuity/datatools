from datatools.jt.llmcodec.base62_utils import to_base62, base62_len

# Token kind constants used in the token table.
KIND_VAR = "#"    # #tag#  — BPE / frequent-pattern token (normal text)
KIND_META = "!"   # !tag!  — BPE / frequent-pattern token (meta / cross-line)
KIND_MACRO = "&"  # &tag   — macro template token


class TokenRegistry:
    """Holds token tables for vars, meta, and macro tokens.

    Manages sequential internal token ID allocation and the token table
    (list of ``(internal_token_str, kind, expansion_str)`` triples).

    Parameters
    ----------
    frequent_tokens:
        Pre-computed frequency dictionary for identifier-like tokens (as
        returned by :func:`build_ident_counts`).  When provided, the
        compressor will substitute frequent identifiers before running BPE.
        Pass ``None`` (or omit) to skip that pass.
    """

    def __init__(self, frequent_tokens: dict[str, int]) -> None:
        self.frequent_tokens = frequent_tokens
        # Sequential counters for internal token IDs (used during compression).
        self._var_idx = 0
        self._meta_idx = 1
        self._macro_idx = 1
        # Token table: list of (internal_token_str, kind, expansion_str).
        # Populated in creation order; reordered at serialisation.
        self.token_table: list[tuple[str, str, str]] = []

    def get_var_token(self) -> str:
        t = f"#{to_base62(self._var_idx)}#"
        self._var_idx += 1
        return t

    def get_meta_token(self) -> str:
        t = f"!{to_base62(self._meta_idx)}!"
        self._meta_idx += 1
        return t

    def get_macro_token(self) -> str:
        t = f"&{to_base62(self._macro_idx)}"
        self._macro_idx += 1
        return t

    def register(self, token: str, kind: str, expansion: str) -> None:
        """Record a token in the table."""
        self.token_table.append((token, kind, expansion))

    def var_tag_len(self) -> int:
        return base62_len(self._var_idx) + 2

    def meta_tag_len(self) -> int:
        return base62_len(self._meta_idx) + 2
