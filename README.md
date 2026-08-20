# EELWizard

EELWizard is a local-first audio-DSP engineering system focused on RootlessJamesDSP LiveProg/EEL2. It is designed to give AI coding agents and human DSP developers a deterministic source-of-truth layer for host compatibility, EEL_VM behavior, known-good implementation patterns, execution, and measurement.

## Current status: M1 knowledge engine

M0 proved the execution loop. M1 adds a deterministic, source-aware knowledge layer on top of it.

EELWizard can currently:

- ingest exactly 40 upstream RootlessJamesDSP factory LiveProg scripts as `SHIPPED/rootless-upstream`, while excluding supplemental SoloConsole material from upstream evidence;
- parse LiveProg metadata, controls, sections, tags, host variables, and source revision;
- reconstruct files from the project repository-digest format without hashing digest separators as source bytes;
- reproduce the pinned EEL_VM `loose_eel.c` Git blob SHA `767d91549cb3bb059c8bdd987f425e9a85b288bf` from the supplied digest;
- extract a deterministic EEL_VM primitive catalog from the pinned VM documentation;
- annotate the upstream corpus with a narrow deterministic technique vocabulary and observed VM primitives;
- report `@init` and `@sample` as `ESTABLISHED` for the complete upstream factory corpus while keeping `@slider` and `@block` at `NOT_ESTABLISHED`;
- retrieve LiveProg examples using text plus exact source-class, host-profile, tag, technique, and VM-primitive filters;
- rerank equal text matches by the project source-authority order before applying the result limit;
- run a deterministic retrieval benchmark that fails closed with a nonzero CLI exit code;
- diagnose and safely repair the M0 missing-semicolon fixture;
- translate `@init`/`@sample` LiveProg sections into standalone core EEL_VM source;
- execute that source through a real EEL_VM CLI; and
- measure the M0 gain vertical slice objectively at **-8.00 dB ± 0.02 dB**.

The M1 development benchmark contains five required upstream retrieval cases: gain, fractional delay, STFT denoise, FFT convolution/HRTF, and polyphase filterbank. The current verified result is **5/5 (100%)** within top 3.

The real M0/M1 regression slice measured `-7.99999998754253 dB` for the expected `-8.0 dB` gain and finished at `MEASUREMENT_PASS`.

## Intended CLI use

After installation, the package exposes the `eelwizard` command. Examples:

```text
eelwizard corpus inspect "gain spl0" --source-class SHIPPED --host-profile rootless-upstream
eelwizard corpus inspect --technique fractional-delay --vm-primitive fractionalDelayLineProcess
eelwizard corpus inspect --tag filter
eelwizard benchmark retrieval --database corpus/generated/corpus.sqlite3 --cases benchmarks/m1_retrieval.json --report reports/m1-retrieval.json
eelwizard doctor --eel-cli path/to/eel_CLI
eelwizard demo gain-slice --eel-cli path/to/eel_CLI --database corpus/generated/corpus.sqlite3
```

## Explicit non-claims

EELWizard does **not** yet claim autonomous DSP design, Asta research integration, semantic/vector retrieval, broad automatic EEL repair, Android device validation, listening approval, or EELVault release automation. M1 annotations are deterministic rules, not model-generated semantic judgments.

`NOT_ESTABLISHED` does not mean `UNSUPPORTED`. In particular, the 40 verified upstream factory scripts establish `@init` and `@sample`; their lack of `@slider` and `@block` cannot by itself prove those sections are rejected by every RootlessJamesDSP host revision.

## Open infrastructure gates

Two repository/release infrastructure items remain outside the demonstrated M1 behavior:

1. `uv.lock` still needs to be generated and committed in an environment with package-registry metadata available, after which CI can use `uv sync --frozen --dev` reproducibly.
2. `051-lab/EELWizard` still needs to be created/published because the GitHub connector available to this chat can modify existing repositories but cannot create a new repository.

For EEL_VM provenance, M1 now proves that digest reconstruction of pinned `loose_eel.c` reproduces GitHub's exact blob SHA. A full 290-file commit-archive comparison is still a stronger optional provenance check and is not claimed complete here.

The approved architecture and milestone plans live under `docs/superpowers/` in this source tree, with the parent design retained in EELVault.
