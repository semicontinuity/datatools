from datatools.jt.llmcodec.base62_utils import to_base62, base62_len
from datatools.jt.llmcodec.global_token_registry import GlobalTokenRegistry
from datatools.jt.llmcodec.string_utils import identifier_counts


class TokenRegistry:
    """Holds token tables for idents, meta, and macro tokens.

    Manages pat→index mappings and the legend
    (list of ``(substitution_str, expansion_str)`` pairs in creation order).

    Parameters
    ----------
    global_registry:
        contains:
            ident -> index (inverted array)
            shared inline/meta/macro token tables
    """
    frequent_idents: dict[str, int]

    def __init__(
        self,
        global_registry: "GlobalTokenRegistry",
    ) -> None:
        self.global_registry = global_registry
        # Legend: list of (substitution_str, expansion_str) in creation order.
        self.legend: list[tuple[str, str]] = []

    def get_ident_substitution(self, pat: str) -> str | None:
        """Return (if present in index) the substitution token for a frequent-identifier pattern."""
        idx = self.global_registry.ident_index.get(pat)
        if idx is not None:
            return f"#{to_base62(idx)}#"
        return None

    def get_inline_substitution(self, pat: str) -> str:
        """Delegate to global_registry."""
        return self.global_registry.get_inline_substitution(pat)

    def get_meta_substitution(self, pat: str) -> str:
        """Delegate to global_registry."""
        return self.global_registry.get_meta_substitution(pat)

    def get_macro_substitution(self, pat: str) -> str:
        """Delegate to global_registry."""
        return self.global_registry.get_macro_substitution(pat)

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
        return self.global_registry.inline_tag_len()

    def meta_tag_len(self) -> int:
        return self.global_registry.meta_tag_len()
