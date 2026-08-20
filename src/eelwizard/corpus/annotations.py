from __future__ import annotations

import re

_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_LANGUAGE_CALLS = {"function", "instance", "local", "loop", "while"}


def _code_region(text: str) -> str:
    match = re.search(r"(?m)^\s*@[A-Za-z_][A-Za-z0-9_]*\s*$", text)
    return text[match.start() :] if match else text


def extract_function_calls(text: str) -> list[str]:
    calls = set(_CALL_RE.findall(_code_region(text)))
    return sorted(calls - _LANGUAGE_CALLS)


def annotate_liveprog(
    name: str,
    tags: list[str],
    text: str,
    primitive_catalog: set[str],
) -> tuple[list[str], list[str]]:
    calls = set(extract_function_calls(text))
    primitives = sorted(calls & primitive_catalog)
    primitive_keys = {primitive.casefold() for primitive in primitives}
    haystack = " ".join([name, *tags]).casefold()
    techniques: set[str] = set()

    if "gain" in haystack:
        techniques.add("gain")
    if "fractionaldelay" in haystack or any(
        primitive.startswith("fractionaldelayline") for primitive in primitive_keys
    ):
        techniques.add("fractional-delay")
    if "stft" in haystack or any(primitive.startswith("stft") for primitive in primitive_keys):
        techniques.add("stft")
    if "fftconvolution" in haystack or any(
        primitive.startswith("conv1d") for primitive in primitive_keys
    ):
        techniques.add("fft-convolution")
    if "polyphasefilterbank" in haystack or any(
        "polyphasefilterbank" in primitive for primitive in primitive_keys
    ):
        techniques.add("polyphase-filterbank")

    if "dcremove" in haystack or "dc_remove" in haystack:
        techniques.add("dc-filter")
    if any(token in haystack for token in ("highpass", "lowpass", "butterworth")) or any(
        primitive.startswith("iirbandsplitter") for primitive in primitive_keys
    ):
        techniques.add("iir-filter")
    if "firfilter" in haystack or any(primitive.startswith("fir") for primitive in primitive_keys):
        techniques.add("fir-filter")
    if any(token in haystack for token in ("bandsplitting", "3bandsplitting", "8bandsplitting")):
        techniques.add("band-splitting")
    if any(token in haystack for token in ("reverb", "verb")):
        techniques.add("reverb")
    if any(token in haystack for token in ("stereo", "widen", "surround", "downmixer", "mscentre")):
        techniques.add("stereo-processing")
    if any(token in haystack for token in ("compander", "dynamicbass")):
        techniques.add("dynamics")
    if any(token in haystack for token in ("distortion", "mangler", "decimate")):
        techniques.add("distortion")

    return sorted(techniques), primitives
