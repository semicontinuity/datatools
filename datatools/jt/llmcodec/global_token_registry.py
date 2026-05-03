from datatools.jt.llmcodec.base62_utils import base62_len, to_base62
from datatools.jt.llmcodec.util import debug


def _ident_tag_len(idx: int) -> int:
    """Length of the substitution token #XX# for a given index."""
    return base62_len(idx) + 2


class GlobalTokenRegistry:
    """Accumulates identifier frequency counts across multiple NDJson instances.

    Usage
    -----
    1. Pass one instance to every :func:`make_ndjson` call.  Each call
       counts identifier occurrences directly into ``ident_counts``.
    2. After all files have been scanned, call :meth:`init` to build the
       shared ident index from the accumulated counts.
    3. Pass ``ident_index`` as ``shared_idents`` to every column compressor
       so that ``#N#`` tokens are consistent across all columns and files.

    Attributes
    ----------
    ident_counts:
        Raw identifier → occurrence count, accumulated across all calls.
    ident_index:
        identifier → token index (pat→index), populated by :meth:`init`.
        Only identifiers that appear more than once *and* whose substitution
        saves space are included.
    """

    def __init__(self) -> None:
        self.ident_counts: dict[str, int] = {}
        self.ident_index: dict[str, int] = {}
        self._inlines: dict[str, int] = {}
        self._metas: dict[str, int] = {}
        self._macros: dict[str, int] = {}

    def init(self) -> None:
        """Build ``ident_index`` from the accumulated ``ident_counts``.

        Sorts candidates by descending frequency, assigns sequential indices,
        and keeps only those where substituting saves space:

            count * (len(pat) - token_len) - (token_len + 3 + len(pat) + 1) > 0
        """
        candidates = sorted(
            (pat for pat, cnt in self.ident_counts.items() if cnt > 1),
            key=lambda p: -self.ident_counts[p],
        )
        index: dict[str, int] = {}
        for pat in candidates:
            idx = len(index)
            token_len = _ident_tag_len(idx)
            count = self.ident_counts[pat]
            definition_overhead = token_len + 3 + len(pat) + 1
            savings = count * (len(pat) - token_len) - definition_overhead
            if savings > 0:
                index[pat] = idx
        self.ident_index = index
        debug(f'Created frequent ident index with size {len(index)}')

    def get_inline_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for an in-line BPE pattern."""
        if pat not in self._inlines:
            self._inlines[pat] = len(self._inlines)
        return f"~{to_base62(self._inlines[pat])}~"

    def get_meta_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for a meta pattern."""
        if pat not in self._metas:
            self._metas[pat] = len(self._metas)
        return f"!{to_base62(self._metas[pat])}!"

    def get_macro_substitution(self, pat: str) -> str:
        """Return (allocating if needed) the substitution token for a macro pattern."""
        if pat not in self._macros:
            self._macros[pat] = len(self._macros)
        return f"&{to_base62(self._macros[pat])}"

    def inline_tag_len(self) -> int:
        return base62_len(len(self._inlines)) + 2  # ~XX~

    def meta_tag_len(self) -> int:
        return base62_len(len(self._metas)) + 2
