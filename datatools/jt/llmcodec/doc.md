# ndjson\_log\_compress — column-oriented log compression

## Rationale

Structured logs are typically stored as NDJSON (one JSON object per line).
Adjacent records share the same set of keys and often share long common
prefixes in their values (timestamps, hostnames, service names, trace IDs,
…).  Compressing the raw NDJSON with a general-purpose byte compressor
(gzip, zstd) works, but the result is opaque: you cannot inspect, grep, or
partially decode it without decompressing the whole stream.

`ndjson_log_compress` produces a **human-readable, grep-friendly** format
that is also significantly smaller than the raw NDJSON:

* Each JSON key becomes its own **column block** — values are stored
  vertically, one per line, so repeated substrings compress well even with
  simple text tools.
* A **common prefix** is factored out of each column and stored once in the
  opening tag.
* A multi-pass **BPE + macro-template** pipeline further reduces repeated
  substrings inside each column.
* Columns that are present in every record (*complete*) are stored
  separately from columns that appear only in some records (*incomplete*).
* The output is plain text; individual columns can be inspected with
  `grep`, `sed`, or a pager without running the decompressor.

The companion tools are:

| Tool | Purpose |
|---|---|
| `ndjson_log_compress` | Compress NDJSON → `<COLUMNS>` format |
| `ndjson_log_decompress` | Decompress `<COLUMNS>` format → NDJSON |
| `ndjson_log_prepare` | Reorder NDJSON keys before compression (optional but recommended) |

---

## Typical workflow

```sh
# 1. (optional) reorder keys so complete columns come first
ndjson_log_prepare < service.ndjson > service_prepared.ndjson

# 2. compress
ndjson_log_compress < service_prepared.ndjson > service.clg

# 3. inspect a single column without decompressing everything
grep -A9999 '^<level>' service.clg | grep -m1 -B9999 '^</level>'

# 4. decompress back to NDJSON
ndjson_log_decompress < service.clg
```

---

## Output format (`<COLUMNS>` syntax)

### Top-level structure

```
<COLUMNS>
<key1 [prefix='…'] [n='N']>
[<LEGEND>
…legend entries…
</LEGEND>]
…data lines…
</key1>
<key2>
…
</key2>
[<>
[<LEGEND>…</LEGEND>]
…incomplete-column data lines…
</>]
<COLUMNS>
```

The file is delimited by `<COLUMNS>` markers (both opening and closing use
the same tag).  Between them, each complete column occupies its own block,
followed by an optional `<>…</>` block for incomplete columns.

### Complete-column block

```
<fieldname [prefix='VALUE'] [n='N']>
[<LEGEND>…</LEGEND>]
line-0
line-1
…
</fieldname>
```

* **`fieldname`** — the JSON key (alphanumeric + `_`).
* **`prefix='VALUE'`** — common prefix factored out of all values.
  Single-quoted; only `\'` needs escaping inside.
  Absent when there is no common prefix.
* **`n='N'`** — present *only* when every value in the column is identical
  to `prefix` (i.e. the body is empty).  `N` is the number of records.
* The body contains one line per record (after stripping the prefix).
  Consecutive identical non-empty lines may be collapsed to `    ... xN`
  (four spaces, `... x`, count) when that saves space.

### Incomplete-column block

```
<>
[<LEGEND>…</LEGEND>]
line-0
line-1
…
</>
```

Each line corresponds to one record (positional alignment).  A line is
empty when the record has none of the incomplete keys.  A non-empty line
contains comma-separated `"key":value` pairs in JSON syntax:

```
"error":"connection refused","retries":3
```

### LEGEND block

```
<LEGEND>
#ab# = some repeated substring
!3! = another repeated substring
&7 = prefix_part?suffix_part
</LEGEND>
```

The legend maps **tokens** to their expansions.  Three token types exist:

| Syntax | Meaning |
|---|---|
| `#tag#` | BPE / frequent-pattern token (normal text) |
| `!tag!` | BPE / frequent-pattern token (meta / cross-line text) |
| `&tag` | Macro template token |

Macro templates contain exactly one `?` placeholder.  When a data line
contains `&tag:#inner#` or `&tag:!inner!`, the decompressor expands
`#inner#` (or `!inner!`) first, then substitutes the result for `?` in the
macro template.  Both the prefix part and the suffix part (the text before
and after `?`) must be non-empty; pure-prefix or pure-suffix templates are
not created because they add overhead without benefit.

Legend values that start and end with `'` are single-quoted strings (the
quotes are stripped before use).

---

## Compression pipeline (per column)

Each column's value list is joined with newlines and passed through the
following stages in order:

1. **Frequent-pattern replacement** — bracket tokens `[…]` and
   `key=`/`key==` patterns that appear more than once are replaced with
   `#tag#` tokens and recorded in the legend.

2. **BPE normal** — byte-pair encoding on alphanumeric/non-alphanumeric
   token boundaries, splitting on `#tag#` separators.  Merges substrings
   that appear across multiple lines.

3. **BPE meta** — byte-pair encoding across line boundaries (splits on
   newlines), targeting substrings that span `#tag#`/`!tag!` tokens.

4. **Macro templating** — for each `#tag#`/`!tag!` occurrence in a line,
   a *template* is formed by replacing that occurrence with `?`.  Templates
   that appear in many lines are assigned a `&macro` token; matching lines
   are rewritten as `&macro:#tag#`.  Only templates with non-empty text on
   both sides of `?` are considered.

5. **Tag-sequence macro templating** — sequences of two or more adjacent
   `#tag#`/`!tag!` tokens are compressed similarly: the first token in the
   sequence is kept as the argument, the rest become the template body.

6. **Deduplication** — consecutive identical non-empty lines are collapsed
   to `    ... xN` when doing so saves bytes.

---

## `ndjson_log_prepare` — key reordering

```sh
ndjson_log_prepare < input.ndjson > output.ndjson
```

Reads NDJSON from stdin, reorders keys in every record so that **complete
keys** (present in all records) come first and **incomplete keys** come
last.  Within each group, keys are ordered by first appearance across the
whole input.  Reordering is applied **recursively** to dict-valued keys.

This is a lossless transformation.  Running it before `ndjson_log_compress`
improves compression because complete columns are stored contiguously and
their common prefixes are longer.

---

## `ndjson_log_decompress` — decompression

```sh
ndjson_log_decompress < file.clg
```

Reads a `<COLUMNS>`-format file from stdin and writes one JSON object per
line to stdout (NDJSON).

The decompressor:

1. Strips the outer `<COLUMNS>` markers.
2. Parses each `<key …>…</key>` block, reads its optional `<LEGEND>`,
   expands tokens, restores the prefix, and reconstructs the value list.
3. Parses the optional `<>…</>` block the same way, then splits each
   expanded line on top-level commas to recover `"key":value` pairs.
4. Assembles records by index and emits them as NDJSON.

---

## Tuning constants (in `ndjson_log_compress`)

| Constant | Default | Meaning |
|---|---|---|
| `BPE_MAX_ITERATIONS` | 100 | Maximum BPE merge rounds per column |
| `BPE_MIN_SAVINGS` | 5 | Minimum byte savings to accept a BPE merge |
| `MACRO_MIN_COUNT` | 4 | Minimum occurrences to consider a macro |
| `MACRO_MIN_TEMPLATE_LEN` | 5 | Minimum template length to consider |
| `MACRO_OVERHEAD_MULT` | 4 | Per-occurrence overhead multiplier for savings calc |
| `MACRO_OVERHEAD_CONST` | 5 | Fixed overhead constant for savings calc |

---

## Limitations

* Input must be valid NDJSON (one JSON **object** per line; arrays and
  scalars are rejected).
* The format is designed for **batch** compression of a fixed record set,
  not for streaming append.
* Key names must match `[A-Za-z0-9_]+` to be stored as complete columns;
  keys with other characters end up in the incomplete section.
* The `?` character is used internally as a placeholder in macro templates.
  It cannot appear in valid JSON string values, so there is no collision
  risk with log data.
