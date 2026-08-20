from __future__ import annotations

from eelwizard.models import (
    FeatureEvidenceState,
    FeatureRecord,
    HostProfile,
    LiveProgRecord,
    SourceClass,
)

_UPSTREAM_FEATURES = ("@init", "@sample", "@slider", "@block")


def build_rootless_upstream_feature_matrix(
    records: list[LiveProgRecord],
    revision: str,
) -> list[FeatureRecord]:
    if len(records) != 40:
        raise ValueError(f"rootless-upstream feature matrix requires exactly 40 records, got {len(records)}")
    if any(
        record.source_class is not SourceClass.SHIPPED
        or record.host_profile is not HostProfile.ROOTLESS_UPSTREAM
        for record in records
    ):
        raise ValueError("feature matrix requires rootless-upstream SHIPPED records only")
    if any(record.source_revision != revision for record in records):
        raise ValueError("feature matrix records must match the requested source revision")

    matrix: list[FeatureRecord] = []
    for feature in _UPSTREAM_FEATURES:
        section = feature[1:]
        evidence = sorted(record.source_path for record in records if section in record.sections)
        state = (
            FeatureEvidenceState.ESTABLISHED
            if evidence
            else FeatureEvidenceState.NOT_ESTABLISHED
        )
        matrix.append(
            FeatureRecord(
                feature=feature,
                host_profile=HostProfile.ROOTLESS_UPSTREAM,
                source_class=SourceClass.SHIPPED,
                state=state,
                evidence=evidence,
                source_revision=revision,
            )
        )
    return matrix
