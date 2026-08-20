# EELWizard M1 Knowledge Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic source-aware knowledge layer that maps host/VM evidence and known-good LiveProg techniques into filterable retrieval with a measurable benchmark.

**Architecture:** Preserve M0's `LiveProgRecord`/`CorpusStore` interfaces while extending records with deterministic annotations and adding separate feature/reference records. Digest ingestion is byte-oriented so provenance hashes are trustworthy. Retrieval remains SQLite/FTS5 and authority-aware; no embeddings or LLM annotations are introduced in M1.

**Tech Stack:** Python 3.11+, Pydantic 2, SQLite/FTS5, Typer, pytest, stdlib `hashlib`/`re`/`json`.

**Spec:** `docs/superpowers/specs/2026-08-20-eelwizard-m1-knowledge-engine.md`

## Global Constraints

- Preserve the M0 gain vertical slice and existing public CLI behavior.
- Authority order is `HOST > VM > SHIPPED > VAULT > SPEC > RESEARCH > REFERENCE > INSPIRATION > ESTIMATE`.
- `rootless-upstream` factory count is exactly 40; `soloconsole.eel` is never upstream `SHIPPED` evidence.
- `@slider`/`@block` under `rootless-upstream` are `NOT_ESTABLISHED`, not `UNSUPPORTED`.
- Canonical M1 annotations are deterministic; no model-generated semantic labels.
- Fail closed: benchmark or provenance checks that did not run are never reported as passed.

---

### Task 1: Provenance and knowledge record contracts

**Files:**
- Modify: `src/eelwizard/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Produces `FeatureEvidenceState`, `FeatureRecord`, `ReferenceRecord`.
- Extends `LiveProgRecord` with `source_revision`, `tags`, `techniques`, and `vm_primitives` using empty/default values so M0 JSON remains readable.

- [ ] **Step 1: Write failing contract tests** asserting legacy `LiveProgRecord` JSON still validates, new annotation defaults are empty, `FeatureEvidenceState` contains `ESTABLISHED` and `NOT_ESTABLISHED`, and `ReferenceRecord` requires provenance fields.
- [ ] **Step 2: Run** `PYTHONPATH=src python -m pytest tests/test_models.py -v` and verify the new tests fail because the contracts do not exist.
- [ ] **Step 3: Implement minimal Pydantic/Enum contracts** in `models.py`; do not change M0 enum values.
- [ ] **Step 4: Re-run the model tests** and then `PYTHONPATH=src python -m pytest -m 'not integration' -q`.
- [ ] **Step 5: Commit** `feat: add M1 knowledge contracts`.

### Task 2: Exact repository-digest parsing and EEL_VM primitive catalog

**Files:**
- Create: `src/eelwizard/corpus/digests.py`
- Create: `src/eelwizard/corpus/references.py`
- Test: `tests/test_digests.py`
- Test: `tests/test_references.py`

**Interfaces:**
- Produces `parse_repository_digest(text: str) -> dict[str, bytes]`.
- Produces `git_blob_sha(content: bytes) -> str`.
- Produces `extract_eel_vm_primitives(readme_text: str) -> list[str]` and `build_eel_vm_reference_records(...) -> list[ReferenceRecord]`.

- [ ] **Step 1: Write a failing digest test** with two synthetic `FILE:` sections proving exactly three inter-section separator newlines are excluded from source bytes.
- [ ] **Step 2: Add the pinned provenance test** using `/mnt/data/EEL_VM_digest.txt`: parsed `loose_eel.c` must be 4979 bytes and hash to Git blob `767d91549cb3bb059c8bdd987f425e9a85b288bf`.
- [ ] **Step 3: Run digest tests and confirm RED.**
- [ ] **Step 4: Implement the digest parser/hash functions** without normalizing line endings or stripping source whitespace beyond the digest's known three-newline separator.
- [ ] **Step 5: Write failing primitive-catalog tests** requiring at least `fft`, `ifft`, `fractionalDelayLineProcess`, `FIRInit`, `FIRProcess`, `Conv1D`, and `IIRBandSplitterProcess` when those identifiers are present in the reference text; output must be sorted/unique.
- [ ] **Step 6: Implement reference extraction and records** with `source_class=VM`, `host_profile=eel-vm-core`, and pinned EEL_VM revision.
- [ ] **Step 7: Run both test files and the full non-integration suite.**
- [ ] **Step 8: Commit** `feat: ingest EEL VM reference knowledge`.

### Task 3: Deterministic LiveProg technique and primitive annotation

**Files:**
- Create: `src/eelwizard/corpus/annotations.py`
- Modify: `src/eelwizard/corpus/liveprog.py`
- Modify: `src/eelwizard/corpus/ingest.py`
- Test: `tests/test_annotations.py`
- Modify: `tests/test_liveprog.py`

**Interfaces:**
- Produces `extract_function_calls(text: str) -> list[str]`.
- Produces `annotate_liveprog(name, tags, text, primitive_catalog) -> tuple[list[str], list[str]]`.
- `normalize_liveprog(..., source_revision: str | None = None, primitive_catalog: set[str] | None = None)` populates the new fields.

- [ ] **Step 1: Write failing tests** for `gainControl`, `fractionalDelayline`, `stftDenoise`, `fftConvolutionHRTF`, and `polyphaseFilterbank` fixtures/snippets. Assertions must cover exact technique labels and detected VM primitives.
- [ ] **Step 2: Run annotation tests and confirm RED.**
- [ ] **Step 3: Implement function-call extraction** with an identifier-before-`(` regex while excluding language keywords such as `function`, `loop`, and `while` from primitive candidates.
- [ ] **Step 4: Implement the fixed vocabulary rules** from the M1 spec using filenames/tags and explicit primitive names; sort/deduplicate output.
- [ ] **Step 5: Wire annotations/source revision/tags into normalization and upstream manifest generation.**
- [ ] **Step 6: Run annotation/liveprog/corpus tests and the full non-integration suite.**
- [ ] **Step 7: Commit** `feat: annotate LiveProg techniques`.

### Task 4: Host feature matrix and source-aware filtered retrieval

**Files:**
- Create: `src/eelwizard/corpus/features.py`
- Modify: `src/eelwizard/corpus/store.py`
- Modify: `src/eelwizard/cli.py`
- Test: `tests/test_features.py`
- Modify: `tests/test_corpus.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces `build_rootless_upstream_feature_matrix(records, revision) -> list[FeatureRecord]`.
- Extends `CorpusStore.search_liveprog(query, limit=5, *, source_class=None, host_profile=None, technique=None, vm_primitive=None)`.
- Adds CLI filters `--source-class`, `--host-profile`, `--technique`, `--vm-primitive` to `corpus inspect`.

- [ ] **Step 1: Write failing feature tests** proving 40 upstream records establish `@init` and `@sample`, while `@slider` and `@block` are `NOT_ESTABLISHED`.
- [ ] **Step 2: Write failing store tests** proving a technique filter returns `fractionalDelayline` for `fractional-delay` and a primitive filter can isolate an STFT/FFT example without admitting wrong host/source classes.
- [ ] **Step 3: Run the tests and confirm RED.**
- [ ] **Step 4: Implement the feature matrix** based only on observed normalized records and explicit M1 policy.
- [ ] **Step 5: Extend the SQLite schema** with indexed source/host plus JSON/text annotation columns; keep `search_liveprog('gainControl')` backward compatible.
- [ ] **Step 6: Implement filtered search and CLI options.** Empty text query with a structural filter must be supported by a non-FTS SQL path.
- [ ] **Step 7: Run feature/corpus/CLI tests and full non-integration suite.**
- [ ] **Step 8: Commit** `feat: add host matrix and filtered retrieval`.

### Task 5: Retrieval benchmark and reproducible M1 demo

**Files:**
- Create: `src/eelwizard/bench.py`
- Create: `benchmarks/m1_retrieval.json`
- Modify: `src/eelwizard/cli.py`
- Create: `tests/test_bench.py`
- Modify: `README.md`

**Interfaces:**
- Produces `RetrievalBenchmarkCase`, `RetrievalBenchmarkResult`, `run_retrieval_benchmark(store, cases)`.
- Adds `eelwizard benchmark retrieval --database ... --cases ... --report ...`.
- Fixed cases require authoritative retrieval of: `gainControl`, `fractionalDelayline`, `stftDenoise`, `fftConvolutionHRTF`, and `polyphaseFilterbank` within top 3, using structural filters where appropriate.

- [ ] **Step 1: Write failing benchmark tests** for one passing and one failing case; failure must cause the CLI command to exit nonzero.
- [ ] **Step 2: Run benchmark tests and confirm RED.**
- [ ] **Step 3: Implement benchmark models/runner and CLI.** Report JSON must include per-case hits, pass/fail, aggregate passed/total, and `pass_rate`.
- [ ] **Step 4: Create the five-case benchmark dataset** with explicit expected names and top-k=3.
- [ ] **Step 5: Build a real 40-file manifest/database from `/mnt/data/live-prog-scripts.zip` after excluding SoloConsole, run the benchmark, and require 5/5.**
- [ ] **Step 6: Re-run the complete non-integration test suite and, if a real EEL_VM binary is available, the M0 integration/gain slice.**
- [ ] **Step 7: Update README with M1 capabilities and exact non-claims.**
- [ ] **Step 8: Commit** `feat: add M1 retrieval benchmark`.

## Final self-review checklist

- Spec coverage: every M1 required output maps to Tasks 1–5.
- Placeholder scan: no `TBD`, `TODO`, “similar to,” or unspecified implementation step is present.
- Type consistency: all new record/filter/benchmark interfaces are introduced before later tasks consume them.
- M0 compatibility: legacy JSON defaults and the original `search_liveprog(query, limit)` call shape are explicitly preserved.


## Execution rulings

- **Task 2:** The original plan named a nonexistent `fir` primitive. Pinned EEL_VM documentation exposes `FIRInit` and `FIRProcess`; those exact names replace `fir`. This is a plan correction against VM authority, not a scope change.
- **Task 4:** The M1 specification explicitly requires tags to be searchable/filterable although the original Task 4 interface omitted a tag filter. The specification wins; exact `tag` filtering and CLI `--tag` were added.
- **Task 4:** Authority reranking must occur before the caller's result limit is applied. Equal text matches are therefore reranked by source authority before slicing to `limit`, preventing a lower-authority row from crowding out an equally relevant authoritative row.
