from eelwizard.models import HostProfile, ProjectState, ProjectStatus, SourceClass


def test_authority_and_profiles_are_stable() -> None:
    assert SourceClass.HOST.rank == 1
    assert SourceClass.SHIPPED.rank == 3
    assert SourceClass.ESTIMATE.rank == 9
    assert HostProfile.ROOTLESS_UPSTREAM.value == "rootless-upstream"
    assert HostProfile.ROOTLESS_051.value == "rootless-051"


def test_project_state_round_trips() -> None:
    state = ProjectState(name="gain-slice", status=ProjectStatus.STATIC_PASS)
    assert ProjectState.model_validate_json(state.model_dump_json()) == state


def test_liveprog_legacy_json_gets_m1_annotation_defaults() -> None:
    from eelwizard.models import LiveProgRecord

    legacy = {
        "name": "gainControl",
        "source_class": "SHIPPED",
        "host_profile": "rootless-upstream",
        "source_path": "gainControl.eel",
        "content_hash": "abc123",
        "sections": ["init", "sample"],
        "host_variables": ["spl0", "spl1"],
        "controls": ["dB"],
        "text": "@init\n@sample",
    }
    record = LiveProgRecord.model_validate(legacy)
    assert record.source_revision is None
    assert record.tags == []
    assert record.techniques == []
    assert record.vm_primitives == []


def test_feature_evidence_states_are_explicit() -> None:
    from eelwizard.models import FeatureEvidenceState

    assert FeatureEvidenceState.ESTABLISHED.value == "ESTABLISHED"
    assert FeatureEvidenceState.NOT_ESTABLISHED.value == "NOT_ESTABLISHED"


def test_reference_record_requires_provenance_fields() -> None:
    from pydantic import ValidationError
    import pytest

    from eelwizard.models import ReferenceRecord

    with pytest.raises(ValidationError):
        ReferenceRecord(id="fft", title="FFT")

    record = ReferenceRecord(
        id="eel-vm:fft",
        title="fft",
        source_class=SourceClass.VM,
        host_profile=HostProfile.EEL_VM_CORE,
        source_revision="284b3da00af91efc3aff6bfc1acefb4e801a8ad6",
        source_path="readme.md",
        content_hash="deadbeef",
        text="fft(start_index, size)",
    )
    assert record.source_class is SourceClass.VM
    assert record.host_profile is HostProfile.EEL_VM_CORE


def test_reference_record_requires_source_revision_specifically() -> None:
    from pydantic import ValidationError
    import pytest

    from eelwizard.models import ReferenceRecord

    with pytest.raises(ValidationError) as exc:
        ReferenceRecord(
            id="eel-vm:fft",
            title="fft",
            source_class=SourceClass.VM,
            host_profile=HostProfile.EEL_VM_CORE,
            source_path="readme.md",
            content_hash="deadbeef",
            text="fft(start_index, size)",
        )
    assert any(error["loc"] == ("source_revision",) for error in exc.value.errors())
