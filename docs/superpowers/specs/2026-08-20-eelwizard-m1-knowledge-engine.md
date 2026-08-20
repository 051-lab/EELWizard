# EELWizard M1 Knowledge Engine Specification

**Status:** implementation specification
**Date:** 2026-08-20
**Parent design:** EELVault `docs/superpowers/specs/2026-08-19-eelwizard-design.md` at commit `fbb5b8ea605b77ab326bbb88f34f2ce5dbb03137`

## Goal

Turn the M0 source-classified LiveProg corpus into a source-aware knowledge engine that can answer three deterministic questions before any model-generated DSP is trusted:

1. Which host/VM features are actually established for a selected profile?
2. Which known-good scripts demonstrate a requested technique or VM primitive?
3. Can retrieval return the expected authoritative examples for a fixed benchmark set?

M1 does not add autonomous DSP design or Asta research. It builds the knowledge substrate those later milestones depend on.

## Required outputs

- Extend normalized LiveProg records with tags, source revision, technique labels, and VM primitive labels.
- Parse repository digests into exact file records without treating digest separators as source bytes.
- Produce an EEL_VM primitive catalog from the pinned EEL_VM `readme.md`/source digest.
- Produce explicit host feature records with evidence state. `@init` and `@sample` are established for `rootless-upstream`; `@slider` and `@block` remain `NOT_ESTABLISHED` for that profile until host-source evidence proves otherwise.
- Keep SoloConsole classified as `VAULT/rootless-051` supplemental material; never use it as upstream host truth.
- Extend SQLite/FTS retrieval so technique names, VM primitives, tags, source class, and host profile are searchable/filterable.
- Add a deterministic retrieval benchmark and CLI report. Benchmark failures must return a nonzero exit code.

## Authority and provenance constraints

- Authority order remains `HOST > VM > SHIPPED > VAULT > SPEC > RESEARCH > REFERENCE > INSPIRATION > ESTIMATE`.
- Every feature/primitive record carries evidence source and revision.
- Absence from the 40 factory scripts means `NOT_ESTABLISHED`, not `UNSUPPORTED`.
- Semantic annotations in M1 are deterministic rule outputs; no LLM-generated labels enter the canonical record.
- M0 vertical-slice behavior must remain passing.

## Initial deterministic technique vocabulary

The first vocabulary is deliberately narrow and evidence-based:

- `gain`
- `dc-filter`
- `iir-filter`
- `fir-filter`
- `band-splitting`
- `fractional-delay`
- `stft`
- `fft-convolution`
- `polyphase-filterbank`
- `reverb`
- `stereo-processing`
- `dynamics`
- `distortion`

Rules may use filenames/tags plus explicit function calls, but must be testable and deterministic.

## M1 completion gate

M1 passes when:

1. all M0 tests still pass;
2. digest parsing reproduces the pinned `loose_eel.c` Git blob SHA `767d91549cb3bb059c8bdd987f425e9a85b288bf` after separator removal;
3. the 40-script upstream manifest remains exactly 40 and excludes SoloConsole;
4. records expose deterministic technique and primitive annotations;
5. the upstream feature matrix reports `@init/@sample = ESTABLISHED` and `@slider/@block = NOT_ESTABLISHED`;
6. retrieval supports source-class/host/technique/primitive filters;
7. the fixed retrieval benchmark achieves 100% pass on its required top-k cases;
8. the gain vertical slice remains `MEASUREMENT_PASS` when a real EEL_VM executable is supplied.
