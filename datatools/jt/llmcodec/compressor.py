import json
import re
from collections import defaultdict

from datatools.jt.llmcodec.token_registry import TokenRegistry

# Tuning parameters for compression
BPE_MAX_ITERATIONS = 100
BPE_MIN_SAVINGS = 5
MACRO_MIN_COUNT = 4
MACRO_MIN_TEMPLATE_LEN = 5
MACRO_OVERHEAD_MULT = 4
MACRO_OVERHEAD_CONST = 5

# Pre-compile static regexes for one-off passes
RE_TAGS = re.compile(r"(~[0-9a-zA-Z]+~|#[0-9a-zA-Z]+#|![0-9a-zA-Z]+!)")


def section(tag: str, body: list[str], attrs: str = "") -> list[str]:
    """Wrap body lines with <tag attrs>...</tag>."""
    open_tag = f"<{tag}{' ' + attrs if attrs else ''}>"
    return [open_tag, *body, f"</{tag}>"]


def _render_legend_block(legend_lines: list[str]) -> list[str]:
    """Wrap legend lines in <LEGEND>...</LEGEND> if non-empty."""
    if not legend_lines:
        return []
    return section("LEGEND", legend_lines)


def calc_savings(count: int, length: int) -> int:
    return (count - 1) * length - MACRO_OVERHEAD_MULT * count - MACRO_OVERHEAD_CONST


def _is_alnum(c: str) -> bool:
    return c.isalnum() or c == "_"


def _tokenize_normal(text: str) -> list[str]:
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        is_alnum = _is_alnum(text[i])
        j = i + 1
        while j < n and _is_alnum(text[j]) == is_alnum:
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def _tokenize_meta(text: str) -> list[str]:
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in ("~", "#"):
            j = i + 1
            while j < n and text[j].isalnum():
                j += 1
            if j < n and text[j] == c:
                tokens.append(text[i:j + 1])
                i = j + 1
                continue
        elif c == "!":
            j = i + 1
            while j < n and text[j].isalnum():
                j += 1
            if j < n and text[j] == "!":
                tokens.append(text[i:j + 1])
                i = j + 1
                continue
        is_alnum = _is_alnum(c)
        j = i + 1
        while j < n:
            nc = text[j]
            if is_alnum:
                if not _is_alnum(nc):
                    break
            else:
                if _is_alnum(nc) or nc in ("~", "#", "!"):
                    break
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def _split_normal(text: str) -> tuple[list[str], list[str]]:
    """Split on ~tag~ (or #tag#) separators, returning (parts, seps)."""
    parts = []
    seps = []
    i = 0
    last_end = 0
    n = len(text)
    while i < n:
        if text[i] in ("~", "#"):
            delim = text[i]
            j = i + 1
            while j < n and text[j].isalnum():
                j += 1
            if n > j > i + 1 and text[j] == delim:
                parts.append(text[last_end:i])
                seps.append(text[i:j + 1])
                last_end = j + 1
                i = j + 1
                continue
        i += 1
    parts.append(text[last_end:])
    return parts, seps


def _split_meta(text: str) -> tuple[list[str], list[str]]:
    """Split on newlines."""
    parts = []
    seps = []
    last_end = 0
    for i, c in enumerate(text):
        if c == "\n":
            parts.append(text[last_end:i])
            seps.append("\n")
            last_end = i + 1
    parts.append(text[last_end:])
    return parts, seps


class Compressor:
    """Compress a block of text using BPE + macro templating.

    Parameters
    ----------
    frequent_tokens:
        Pre-computed frequency dictionary for identifier-like tokens (as
        returned by :func:`build_ident_counts`).  When provided, the
        compressor will substitute frequent identifiers before running BPE.
        Pass ``None`` (or omit) to skip that pass.
    """

    _registry: TokenRegistry

    def __init__(self, registry: TokenRegistry):
        self._registry = registry

    @staticmethod
    def _bpe_tokenize_parts(
        part_strings: list[str],
        tokenize_fn,
        id_to_str: list[str],
        str_to_id: dict[str, int],
    ) -> list[list[int]]:
        """Convert string parts into token-id sequences."""
        def get_or_add(s: str) -> int:
            if s not in str_to_id:
                idx = len(id_to_str)
                id_to_str.append(s)
                str_to_id[s] = idx
            return str_to_id[s]

        parts: list[list[int]] = []
        for p in part_strings:
            if not p:
                parts.append([])
            else:
                parts.append([get_or_add(tok) for tok in tokenize_fn(p)])
        return parts

    @staticmethod
    def _bpe_count_ngrams(
        parts: list[list[int]],
        id_to_str: list[str],
        max_n: int,
        min_trim_len: int,
        requires_hash: bool,
    ) -> dict[tuple[int, ...], int]:
        """Count valid n-gram occurrences across all parts."""
        counts: dict[tuple[int, ...], int] = defaultdict(int)
        for part in parts:
            part_len = len(part)
            if part_len < 2:
                continue
            for n in range(2, min(max_n, part_len) + 1):
                for i in range(part_len - n + 1):
                    slc = tuple(part[i:i + n])
                    has_hash = False
                    total_len = 0
                    valid = True
                    for sid in slc:
                        s = id_to_str[sid]
                        if "\n" in s or "\r" in s:
                            valid = False
                            break
                        if requires_hash and ("~" in s or "#" in s or "!" in s):
                            has_hash = True
                        total_len += len(s)
                    if not valid:
                        continue
                    if requires_hash and not has_hash:
                        continue
                    first_s = id_to_str[slc[0]]
                    last_s = id_to_str[slc[-1]]
                    trim_len = (
                        total_len
                        - (len(first_s) - len(first_s.lstrip()))
                        - (len(last_s) - len(last_s.rstrip()))
                    )
                    if trim_len >= min_trim_len:
                        counts[slc] += 1
        return counts

    @staticmethod
    def _bpe_best_slice(
        counts: dict[tuple[int, ...], int],
        id_to_str: list[str],
        tag_len_fn,
    ) -> tuple[tuple[int, ...] | None, int]:
        """Find the n-gram slice with the best savings."""
        best_slice: tuple[int, ...] | None = None
        best_savings = 0
        for slc, count in counts.items():
            if count > 1:
                phrase_len = sum(len(id_to_str[sid]) for sid in slc)
                tag_len = tag_len_fn()
                savings = count * (phrase_len - tag_len) - (tag_len + 3 + phrase_len)
                if savings > best_savings:
                    best_savings = savings
                    best_slice = slc
        return best_slice, best_savings

    @staticmethod
    def _bpe_apply_merge(
        parts: list[list[int]],
        best_slice: tuple[int, ...],
        new_id: int,
    ) -> None:
        """Replace all occurrences of best_slice in parts with new_id in-place."""
        best_slice_len = len(best_slice)
        for idx, part in enumerate(parts):
            if len(part) < best_slice_len:
                continue
            new_part = []
            i = 0
            while i <= len(part) - best_slice_len:
                if tuple(part[i:i + best_slice_len]) == best_slice:
                    new_part.append(new_id)
                    i += best_slice_len
                else:
                    new_part.append(part[i])
                    i += 1
            new_part.extend(part[i:])
            parts[idx] = new_part

    def _run_bpe(
        self,
        text: str,
        max_iter: int,
        tokenize_fn,
        split_fn,
        max_n: int,
        min_trim_len: int,
        requires_hash: bool,
        tag_len_fn,
        next_token_fn,
    ) -> str:
        id_to_str: list[str] = []
        str_to_id: dict[str, int] = {}

        part_strings, seps = split_fn(text)
        parts = self._bpe_tokenize_parts(part_strings, tokenize_fn, id_to_str, str_to_id)

        for _ in range(max_iter):
            counts = self._bpe_count_ngrams(parts, id_to_str, max_n, min_trim_len, requires_hash)
            best_slice, best_savings = self._bpe_best_slice(counts, id_to_str, tag_len_fn)

            if best_savings < BPE_MIN_SAVINGS or best_slice is None:
                break

            best_str = "".join(id_to_str[sid] for sid in best_slice)
            display = f"'{best_str}'" if best_str.startswith(" ") or best_str.endswith(" ") else best_str
            token = next_token_fn(display)

            new_id = len(id_to_str)
            id_to_str.append(token)
            str_to_id[token] = new_id

            self._bpe_apply_merge(parts, best_slice, new_id)

            self._registry.add_legend(token, display)

        result_parts = []
        for i, part in enumerate(parts):
            s = "".join(id_to_str[sid] for sid in part)
            if i < len(seps):
                s += seps[i]
            result_parts.append(s)
        return "".join(result_parts)

    def _run_bpe_normal(self, text: str) -> str:
        return self._run_bpe(
            text,
            BPE_MAX_ITERATIONS,
            _tokenize_normal,
            _split_normal,
            max_n=20,
            min_trim_len=4,
            requires_hash=False,
            tag_len_fn=self._registry.inline_tag_len,
            next_token_fn=self._registry.get_inline_substitution,
        )

    def _run_bpe_meta(self, text: str) -> str:
        return self._run_bpe(
            text,
            BPE_MAX_ITERATIONS,
            _tokenize_meta,
            _split_meta,
            max_n=15,
            min_trim_len=5,
            requires_hash=True,
            tag_len_fn=self._registry.meta_tag_len,
            next_token_fn=self._registry.get_meta_substitution,
        )

    def _process_templates(
        self,
        templates: dict[str, list[tuple[int, str]]],
        lines: list[str],
    ) -> None:
        scores = [
            (t, len(m), calc_savings(len(m), len(t)))
            for t, m in templates.items()
            if calc_savings(len(m), len(t)) > 0 or len(m) >= MACRO_MIN_COUNT
        ]
        scores.sort(key=lambda x: (-len(x[0]), -x[1]))
        templated = [False] * len(lines)

        for template, _, _ in scores:
            matches = templates.get(template)
            if not matches:
                continue
            valid = [(i, ident) for i, ident in matches if not templated[i]]
            if len(valid) > 1:
                macro_tag = self._registry.get_macro_substitution(template)
                self._registry.add_legend(macro_tag, template)
                for i, ident in valid:
                    lines[i] = f"{macro_tag}:{ident}"
                    templated[i] = True

    # Placeholder used in macro templates.
    # '?' cannot appear in valid JSON values (it is not a special JSON char)
    # and is visually clear as a "identifier slot" marker.
    _PLACEHOLDER = "?"

    def _run_macro_templating(self, text: str) -> str:
        lines = [line.rstrip() for line in text.split("\n")]
        templates: dict[str, list[tuple[int, str]]] = defaultdict(list)

        for i, line in enumerate(lines):
            if not line.strip():
                continue
            for m in RE_TAGS.finditer(line):
                pre = line[:m.start()]
                suf = line[m.end():]
                # Only create a template when there is non-empty content on
                # both sides of the placeholder; a pure-prefix or pure-suffix
                # template adds overhead without benefit.
                if not pre or not suf:
                    continue
                template = pre + self._PLACEHOLDER + suf
                if len(template) >= MACRO_MIN_TEMPLATE_LEN:
                    templates[template].append((i, m.group()))

        self._process_templates(templates, lines)
        return "\n".join(lines)

    def _run_tag_sequence_macro_templating(self, text: str) -> str:
        # The lookbehind (?<![0-9a-zA-Z:]) ensures we never match a tag that
        # is already the argument of an existing &macro:tag token (where the
        # character immediately before the opening ~, # or ! would be ':').
        re_seq = re.compile(
            r"(?<![0-9a-zA-Z:])(?:(?:~[0-9a-zA-Z]+~|#[0-9a-zA-Z]+#|![0-9a-zA-Z]+!)[ \t]*){2,}"
        )
        templates: dict[str, int] = defaultdict(int)

        for mat in re_seq.finditer(text):
            seq = mat.group().rstrip()
            for tag_mat in RE_TAGS.finditer(seq):
                pre = seq[:tag_mat.start()]
                suf = seq[tag_mat.end():]
                # Require non-empty content on both sides of the placeholder.
                if not pre or not suf:
                    continue
                template = pre + self._PLACEHOLDER + suf
                templates[template] += 1

        scores = [
            (t, c, calc_savings(c, len(t)))
            for t, c in templates.items()
            if calc_savings(c, len(t)) > 0 or c >= MACRO_MIN_COUNT
        ]
        scores.sort(key=lambda x: (-len(x[0]), -x[1]))

        for template, _, _ in scores:
            parts = template.split(self._PLACEHOLDER)
            if len(parts) != 2:
                continue
            # Use a lookbehind in the substitution regex too, so we never
            # replace a tag that is already a macro argument.
            re_str = (
                r"(?<![0-9a-zA-Z:])"
                + re.escape(parts[0])
                + r"([~#!])([0-9a-zA-Z]+)\1"
                + re.escape(parts[1])
            )
            try:
                compiled = re.compile(re_str)
            except re.error:
                continue
            count = len(compiled.findall(text))
            if calc_savings(count, len(template)) > 0 or count >= MACRO_MIN_COUNT:
                macro_tag = self._registry.get_macro_substitution(template)
                self._registry.add_legend(macro_tag, template)
                text = compiled.sub(f"{macro_tag}:" + r"\1\2\1", text)

        return text

    @staticmethod
    def _annotation(dup_count: int) -> str:
        return f"    ... x{dup_count + 1}"

    @staticmethod
    def _dedup_saves(line: str, dup_count: int) -> bool:
        """Return True if collapsing dup_count extra copies saves space."""
        annotation = f"    ... x{dup_count + 1}"
        # dup_count extra copies cost dup_count*(len(line)+1) chars (with newlines)
        # annotation costs len(annotation)+1 chars
        return dup_count * (len(line) + 1) > len(annotation) + 1

    def _deduplicate_lines(self, text: str) -> list[str]:
        """Collapse consecutive identical non-empty lines when it saves space.

        Empty lines are preserved as-is (they represent values equal to the
        column prefix and must stay in their positional slots).
        """
        final_lines = []
        dup_count = 0
        last_nonempty = ""

        for line in text.split("\n"):
            if not line:
                # Flush any pending dedup run first, then emit the empty line.
                if dup_count > 0:
                    if self._dedup_saves(last_nonempty, dup_count):
                        final_lines.append(self._annotation(dup_count))
                    else:
                        for _ in range(dup_count):
                            final_lines.append(last_nonempty)
                    dup_count = 0
                    last_nonempty = ""
                final_lines.append(line)
                continue
            if line == last_nonempty:
                dup_count += 1
                continue
            if dup_count > 0:
                if self._dedup_saves(last_nonempty, dup_count):
                    final_lines.append(self._annotation(dup_count))
                else:
                    for _ in range(dup_count):
                        final_lines.append(last_nonempty)
                dup_count = 0
            final_lines.append(line)
            last_nonempty = line

        if dup_count > 0:
            if self._dedup_saves(last_nonempty, dup_count):
                final_lines.append(self._annotation(dup_count))
            else:
                for _ in range(dup_count):
                    final_lines.append(last_nonempty)
        return final_lines

    def compress_text(self, text: str) -> tuple[list[str], list[str]]:
        """Compress text and return (legend_lines, data_lines).

        If text contains only empty lines (all values equal the column prefix),
        skip the compression pipeline and return the empty lines directly.
        """
        if not text:
            return [], []

        # If every line is empty (all values == prefix), skip compression.
        lines = text.split("\n")
        if all(not line for line in lines):
            return [], lines

        text = self._registry.replace_frequent_idents(text)

        text = self._run_bpe_normal(text)
        text = self._run_bpe_meta(text)
        text = self._run_macro_templating(text)
        text = self._run_tag_sequence_macro_templating(text)

        data_lines = self._deduplicate_lines(text)
        legend_lines = [f"{sub} = {exp}" for sub, exp in self._registry.legend]
        return legend_lines, data_lines
