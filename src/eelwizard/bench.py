from __future__ import annotations

from pydantic import BaseModel, Field

from eelwizard.corpus.store import CorpusStore
from eelwizard.models import HostProfile, SourceClass


class RetrievalBenchmarkCase(BaseModel):
    id: str
    query: str = ""
    expected_name: str
    top_k: int = Field(default=3, ge=1)
    source_class: SourceClass | None = None
    host_profile: HostProfile | None = None
    technique: str | None = None
    vm_primitive: str | None = None


class RetrievalBenchmarkCaseResult(BaseModel):
    id: str
    expected_name: str
    hits: list[str]
    passed: bool


class RetrievalBenchmarkResult(BaseModel):
    cases: list[RetrievalBenchmarkCaseResult]
    passed: int
    total: int
    pass_rate: float

    @property
    def all_passed(self) -> bool:
        return self.total > 0 and self.passed == self.total


def run_retrieval_benchmark(
    store: CorpusStore,
    cases: list[RetrievalBenchmarkCase],
) -> RetrievalBenchmarkResult:
    results: list[RetrievalBenchmarkCaseResult] = []
    for case in cases:
        hits = store.search_liveprog(
            case.query,
            limit=case.top_k,
            source_class=case.source_class,
            host_profile=case.host_profile,
            technique=case.technique,
            vm_primitive=case.vm_primitive,
        )
        names = [hit.record.name for hit in hits]
        results.append(
            RetrievalBenchmarkCaseResult(
                id=case.id,
                expected_name=case.expected_name,
                hits=names,
                passed=case.expected_name in names,
            )
        )
    passed = sum(result.passed for result in results)
    total = len(results)
    return RetrievalBenchmarkResult(
        cases=results,
        passed=passed,
        total=total,
        pass_rate=(passed / total if total else 0.0),
    )
