from eelwizard.corpus.annotations import annotate_liveprog, extract_function_calls


def test_function_call_extraction_ignores_liveprog_preamble() -> None:
    text = """desc: Gain control
dB:-8<-30,15,1>Volume gain (dB)
@init
gainLin = exp(dB);
@sample
spl0 *= gainLin;
"""
    assert extract_function_calls(text) == ["exp"]


def test_gain_control_annotation() -> None:
    techniques, primitives = annotate_liveprog(
        "gainControl", [], "@init\ng = exp(-1);\n@sample\nspl0 *= g;", {"exp"}
    )
    assert techniques == ["gain"]
    assert primitives == ["exp"]


def test_fractional_delay_annotation() -> None:
    text = """@init
req = fractionalDelayLineInit(0, 1024);
fractionalDelayLineSetDelay(0, 15.1);
@sample
spl0 = fractionalDelayLineProcess(0, spl0);
"""
    catalog = {
        "fractionalDelayLineInit",
        "fractionalDelayLineSetDelay",
        "fractionalDelayLineProcess",
    }
    techniques, primitives = annotate_liveprog("fractionalDelayline", [], text, catalog)
    assert techniques == ["fractional-delay"]
    assert primitives == sorted(catalog)


def test_stft_annotation() -> None:
    text = "@init\nstftInit(0, 1024);\n@sample\nstftForward(0, spl0);"
    techniques, primitives = annotate_liveprog(
        "stftDenoise", [], text, {"stftInit", "stftForward"}
    )
    assert techniques == ["stft"]
    assert primitives == ["stftForward", "stftInit"]


def test_fft_convolution_annotation() -> None:
    text = "@init\nid = Conv1DInit(512, 64, 0);\n@sample\nspl0 = Conv1DProcess(id, spl0);"
    techniques, primitives = annotate_liveprog(
        "fftConvolutionHRTF", [], text, {"Conv1DInit", "Conv1DProcess"}
    )
    assert techniques == ["fft-convolution"]
    assert primitives == ["Conv1DInit", "Conv1DProcess"]


def test_polyphase_filterbank_annotation() -> None:
    text = "@init\nInitPolyphaseFilterbank(0, 8);\n@sample\nPolyphaseFilterbankAnalysisStereo(0, spl0, spl1);"
    catalog = {"InitPolyphaseFilterbank", "PolyphaseFilterbankAnalysisStereo"}
    techniques, primitives = annotate_liveprog("polyphaseFilterbank", [], text, catalog)
    assert techniques == ["polyphase-filterbank"]
    assert primitives == sorted(catalog)
