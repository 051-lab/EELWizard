from eelwizard.corpus.features import build_rootless_upstream_feature_matrix
from eelwizard.models import FeatureEvidenceState, HostProfile, LiveProgRecord, SourceClass

PIN = "60d25ae8a53c6f4691c090673df290a73c6b6357"


def _record(index: int) -> LiveProgRecord:
    return LiveProgRecord(
        name=f"factory-{index}",
        source_class=SourceClass.SHIPPED,
        host_profile=HostProfile.ROOTLESS_UPSTREAM,
        source_path=f"factory-{index}.eel",
        source_revision=PIN,
        content_hash=f"hash-{index}",
        sections=["init", "sample"],
    )


def test_upstream_feature_matrix_distinguishes_observed_from_not_established() -> None:
    matrix = build_rootless_upstream_feature_matrix([_record(i) for i in range(40)], PIN)
    by_feature = {item.feature: item for item in matrix}

    assert by_feature["@init"].state is FeatureEvidenceState.ESTABLISHED
    assert by_feature["@sample"].state is FeatureEvidenceState.ESTABLISHED
    assert by_feature["@slider"].state is FeatureEvidenceState.NOT_ESTABLISHED
    assert by_feature["@block"].state is FeatureEvidenceState.NOT_ESTABLISHED
    assert all(item.host_profile is HostProfile.ROOTLESS_UPSTREAM for item in matrix)
    assert all(item.source_class is SourceClass.SHIPPED for item in matrix)
    assert all(item.source_revision == PIN for item in matrix)


def test_upstream_feature_matrix_refuses_incomplete_corpus() -> None:
    import pytest

    with pytest.raises(ValueError, match="exactly 40"):
        build_rootless_upstream_feature_matrix([_record(i) for i in range(39)], PIN)


def test_upstream_feature_matrix_refuses_foreign_provenance() -> None:
    import pytest

    records = [_record(i) for i in range(40)]
    records[-1] = records[-1].model_copy(
        update={"host_profile": HostProfile.ROOTLESS_051}
    )
    with pytest.raises(ValueError, match="rootless-upstream SHIPPED"):
        build_rootless_upstream_feature_matrix(records, PIN)


def test_upstream_feature_matrix_refuses_wrong_revision() -> None:
    import pytest

    records = [_record(i) for i in range(40)]
    records[-1] = records[-1].model_copy(update={"source_revision": "wrong"})
    with pytest.raises(ValueError, match="source revision"):
        build_rootless_upstream_feature_matrix(records, PIN)
