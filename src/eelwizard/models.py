from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SourceClass(str, Enum):
    HOST = "HOST"
    VM = "VM"
    SHIPPED = "SHIPPED"
    VAULT = "VAULT"
    SPEC = "SPEC"
    RESEARCH = "RESEARCH"
    REFERENCE = "REFERENCE"
    INSPIRATION = "INSPIRATION"
    ESTIMATE = "ESTIMATE"

    @property
    def rank(self) -> int:
        return list(type(self)).index(self) + 1


class HostProfile(str, Enum):
    ROOTLESS_UPSTREAM = "rootless-upstream"
    ROOTLESS_051 = "rootless-051"
    EEL_VM_CORE = "eel-vm-core"
    JDSP_LINUX = "jdsp-linux"


class ProjectStatus(str, Enum):
    DESIGN_ONLY = "DESIGN_ONLY"
    CODE_GENERATED = "CODE_GENERATED"
    STATIC_PASS = "STATIC_PASS"
    VM_PASS = "VM_PASS"
    MEASUREMENT_PASS = "MEASUREMENT_PASS"
    DEVICE_PASS = "DEVICE_PASS"
    LISTENING_APPROVED = "LISTENING_APPROVED"
    EELVAULT_CANDIDATE = "EELVAULT_CANDIDATE"
    RELEASED = "RELEASED"


class FeatureEvidenceState(str, Enum):
    ESTABLISHED = "ESTABLISHED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


class DiagnosticSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Diagnostic(BaseModel):
    code: str
    severity: DiagnosticSeverity
    message: str
    line: int | None = None
    column: int | None = None


class Claim(BaseModel):
    id: str
    value: Any
    unit: str | None = None
    provenance: str
    source: str | None = None
    verification: str | None = None


class FeatureRecord(BaseModel):
    feature: str
    host_profile: HostProfile
    source_class: SourceClass
    state: FeatureEvidenceState
    evidence: list[str] = Field(default_factory=list)
    source_revision: str | None = None


class ReferenceRecord(BaseModel):
    id: str
    title: str
    source_class: SourceClass
    host_profile: HostProfile | None = None
    source_revision: str
    source_path: str
    content_hash: str
    text: str


class LiveProgRecord(BaseModel):
    name: str
    source_class: SourceClass
    host_profile: HostProfile
    source_path: str
    content_hash: str
    source_revision: str | None = None
    sections: list[str] = Field(default_factory=list)
    host_variables: list[str] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    techniques: list[str] = Field(default_factory=list)
    vm_primitives: list[str] = Field(default_factory=list)
    text: str = ""


class ProjectState(BaseModel):
    name: str
    status: ProjectStatus = ProjectStatus.DESIGN_ONLY
    claims: list[Claim] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)
