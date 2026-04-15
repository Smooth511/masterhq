# Dancesong.txt Chunking — Diff Stats Explanation

## Why the diff shows +827 / −308

The original `Dancesong.txt` had **308 lines**, but some of those lines were
extremely long (the longest was **286,019 characters** — a single ~286 KB line of
escaped JSON). Text renderers (CoreText, etc.) crash or get killed by the OS
watchdog when they try to lay out glyphs for lines that long.

The fix split every line longer than 4,000 characters at that boundary and
distributed the result across 11 chunk files. Splitting those long lines turned
308 original lines into **827 shorter lines** — hence **+827 insertions, −308
deletions** in the diff.

## Content integrity verification

| Metric | Original `Dancesong.txt` | Concatenated chunks |
|---|---|---|
| Text characters (newlines stripped) | 2,134,615 | 2,134,615 |
| Total bytes on disk | 2,134,922 | 2,135,441 |
| Line count (git) | 308 | 827 |
| Max line length | 286,019 chars | 4,000 chars |
| Files | 1 | 11 |

- **Byte difference**: 2,135,441 − 2,134,922 = **519 bytes**, which equals exactly
  the **519 newline characters** added by splitting long lines (827 − 308 = 519).
- **Binary comparison**: After stripping newlines from both the original and the
  concatenated chunks, `diff` reports **zero differences** — the text content is
  identical.

### Reproduction

```bash
# Requires Bash (uses process substitution)
# character-level match (strip newlines, compare)
diff <(git show main:Dancesong.txt | tr -d '\n') \
     <(cat Dancesong_chunk_*.txt  | tr -d '\n')
# expected: no output (files are identical)
```
