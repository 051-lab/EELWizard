# EELWizard

EELWizard is a local-first audio-DSP engineering system focused on RootlessJamesDSP LiveProg/EEL2.

## M0 status

The first milestone is deterministic infrastructure, not an autonomous LLM agent. EELWizard can currently:

- index a source-classified RootlessJamesDSP LiveProg corpus;
- keep upstream `SHIPPED` material separate from supplemental project material such as SoloConsole;
- retrieve a known-good `gainControl` implementation;
- diagnose and safely repair one conservative missing-semicolon defect;
- translate `@init`/`@sample` LiveProg sections into standalone core EEL_VM source;
- execute that standalone program through a real EEL_VM CLI; and
- verify the default gain objectively at **-8.00 dB ± 0.02 dB**.

The real M0 vertical slice measured `-7.99999999 dB` in the current development environment.

EELWizard does **not** yet claim autonomous DSP design, Asta research integration, broad EEL repair, Android device validation, or EELVault release automation.

## Open M0 release gates

Two infrastructure checks remain before M0 can be called fully reproducible/release-ready:

1. Generate and commit `uv.lock` in a network-enabled environment, then switch CI back to `uv sync --frozen --dev`.
2. Verify the EEL_VM source used for integration directly against pinned commit `284b3da00af91efc3aff6bfc1acefb4e801a8ad6`. The current local integration used the supplied EEL_VM source digest and executed real EEL_VM code, but its exact commit identity has not yet been cryptographically established.

The approved architecture and implementation plan remain authoritative in EELVault under `docs/superpowers/specs/` and `docs/superpowers/plans/`.
