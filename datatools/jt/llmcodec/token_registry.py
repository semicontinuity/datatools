from datatools.jt.llmcodec.base62_utils import to_base62, base62_len

# Token kind constants used in the token table.
KIND_VAR = "#"    # #tag#  — BPE / frequent-pattern token (normal text)
KIND_META = "!"   # !tag!  — BPE / frequent-pattern token (meta / cross-line)
KIND_MACRO = "&"  # &tag   — macro template token


def _var_substitution(idx: int) -> str:
    return f"#{to_base62(idx)}#"


def _meta_substitution(idx: int) -> str:
    return f"!{to_base62(idx)}!"


def _macro_substitution(idx: int) -> str:
    return f"&{to_base62(idx)}"


class TokenRegistry:
    """Holds token tables for vars, meta, and macro tokens.

    Manages pat→index mappings and the token table
    (list of ``(substitution_str, kind, expansion_str)`` triples).

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
        # pat -> index dicts for each token kind.
        self._vars: dict[str, int] = {}
        self._metas: dict[str, int] = {}
        self._macros: dict[str, int] = {}
        # Sequential counters for internal token IDs (used during compression).
        self._var_idx = 0
        self._meta_idx = 1
        self._macro_idx = 1
        # Token table: list of (substitution_str, kind, expansion_str).
        # Populated in creation order; reordered at serialisation.
        self.token_table: list[tuple[str, str, str]] = []

    def get_var_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for a var pattern."""
        if pat not in self._vars:
            self._vars[pat] = self._var_idx
            self._var_idx += 1
        return _var_substitution(self._vars[pat])

    def get_meta_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for a meta pattern."""
        if pat not in self._metas:
            self._metas[pat] = self._meta_idx
            self._meta_idx += 1
        return _meta_substitution(self._metas[pat])

    def get_macro_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for a macro pattern."""
        if pat not in self._macros:
            self._macros[pat] = self._macro_idx
            self._macro_idx += 1
        return _macro_substitution(self._macros[pat])

    def register(self, substitution: str, kind: str, expansion: str) -> None:
        """Record a token in the table."""
        self.token_table.append((substitution, kind, expansion))

    def var_tag_len(self) -> int:
        return base62_len(self._var_idx) + 2

    def meta_tag_len(self) -> int:
        return base62_len(self._meta_idx) + 2

    def replace_frequent_tokens(self, text: str) -> str:
        """Replace frequent identifiers with tokens, skipping non-saving ones."""
        sorted_token_counts = sorted(self.frequent_tokens.items(), key=lambda x: -x[1])
        for pat, count in sorted_token_counts:
            token_len = self.var_tag_len()  # len of #XX#
            # definition line: "token = pat\n"
            definition_overhead = token_len + 3 + len(pat) + 1
            savings = count * (len(pat) - token_len) - definition_overhead
            if savings <= 0:
                continue
            substitution = self.get_var_substitution(pat)
            text = text.replace(pat, substitution)
            self.register(substitution, KIND_VAR, pat)
        return text
