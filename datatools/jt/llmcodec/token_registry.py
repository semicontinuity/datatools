from datatools.jt.llmcodec.base62_utils import to_base62, base62_len
from datatools.jt.llmcodec.global_token_registry import GlobalTokenRegistry
from datatools.jt.llmcodec.string_utils import identifier_counts


def _macro_substitution(idx: int) -> str:
    return f"&{to_base62(idx)}"


class TokenRegistry:
    """Holds token tables for idents, meta, and macro tokens.

    Manages pat→index mappings and the legend
    (list of ``(substitution_str, expansion_str)`` pairs in creation order).

    Parameters
    ----------
    frequent_tokens:
        ident -> count
    global_registry:
        contains:
            ident -> index (inverted array)
    """
    frequent_idents: dict[str, int]

    def __init__(
        self,
        global_registry: "GlobalTokenRegistry",
    ) -> None:
        self.global_registry = global_registry

        self._inlines: dict[str, int] = {}
        self._metas: dict[str, int] = {}
        self._macros: dict[str, int] = {}
        # Sequential counters for internal token IDs (used during compression).
        # Legend: list of (substitution_str, expansion_str) in creation order.
        self.legend: list[tuple[str, str]] = []

    def get_ident_substitution(self, pat: str) -> str | None:
        """Return (if present in index) the substitution token for a frequent-identifier pattern."""
        idents_dict = self.global_registry.ident_index
        idx = idents_dict.get(pat)
        if idx is not None:
            return f"#{to_base62(idx)}#"
        return None

    def get_inline_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for an in-line BPE pattern."""
        if pat not in self._inlines:
            self._inlines[pat] = len(self._inlines)
        idx = self._inlines[pat]
        return f"~{to_base62(idx)}~"

    def get_meta_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for a meta pattern."""
        if pat not in self._metas:
            self._metas[pat] = len(self._metas)
        idx = self._metas[pat]
        return f"!{to_base62(idx)}!"

    def get_macro_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for a macro pattern."""
        if pat not in self._macros:
            self._macros[pat] = len(self._macros)
        idx = self._macros[pat]
        return f"&{to_base62(idx)}"

    def populate_frequent_idents_from_text(self, text: str) -> None:
        """Compute frequent_tokens from *text*, keeping only tokens with positive savings, sorted by ident index."""
        token_len = self.ident_tag_len()
        result = {}
        for p, c in identifier_counts(text).items():
            if c <= 1:
                continue
            definition_overhead = token_len + 3 + len(p) + 1
            if c * (len(p) - token_len) - definition_overhead > 0:
                result[p] = c

        self.frequent_idents = {p: c for p, c in sorted(result.items(), key=lambda kv: self.global_registry.ident_index[kv[0]])}

    def replace_frequent_idents(self, text: str) -> str:
        """Replace frequent identifiers with their substitution tokens."""
        for ident in self.frequent_idents:
            substitution = self.get_ident_substitution(ident)
            if substitution is None:
                continue
            text = text.replace(ident, substitution)
            self.add_legend(substitution, ident)
        return text

    def add_legend(self, substitution: str, expansion: str) -> None:
        """Record a token in the legend."""
        self.legend.append((substitution, expansion))

    def ident_tag_len(self) -> int:
        return base62_len(len(self.global_registry.ident_index)) + 2  # #XX#

    def inline_tag_len(self) -> int:
        return base62_len(len(self._inlines)) + 2  # ~XX~

    def meta_tag_len(self) -> int:
        return base62_len(len(self._metas)) + 2
