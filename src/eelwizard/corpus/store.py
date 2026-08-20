from dataclasses import dataclass
from pathlib import Path
import sqlite3

from eelwizard.models import HostProfile, LiveProgRecord, SourceClass


@dataclass(frozen=True)
class SearchHit:
    record: LiveProgRecord
    text_score: float
    authority_rank: int


class CorpusStore:
    def __init__(self, path: Path):
        self.path = path

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.path)

    def rebuild(self, records: list[LiveProgRecord]) -> None:
        with self._connect() as db:
            db.executescript(
                """
                DROP TABLE IF EXISTS records;
                DROP TABLE IF EXISTS records_fts;
                CREATE TABLE records (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_class TEXT NOT NULL,
                    host_profile TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    techniques TEXT NOT NULL,
                    vm_primitives TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE INDEX records_source_host_idx
                    ON records(source_class, host_profile);
                CREATE VIRTUAL TABLE records_fts USING fts5(name, text);
                """
            )
            for record in records:
                cursor = db.execute(
                    """
                    INSERT INTO records(
                        name, source_class, host_profile, tags, techniques, vm_primitives, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.name,
                        record.source_class.value,
                        record.host_profile.value,
                        "\n".join(record.tags),
                        "\n".join(record.techniques),
                        "\n".join(record.vm_primitives),
                        record.model_dump_json(),
                    ),
                )
                db.execute(
                    "INSERT INTO records_fts(rowid, name, text) VALUES (?, ?, ?)",
                    (cursor.lastrowid, record.name, record.text),
                )

    def search_liveprog(
        self,
        query: str,
        limit: int = 5,
        *,
        source_class: SourceClass | None = None,
        host_profile: HostProfile | None = None,
        tag: str | None = None,
        technique: str | None = None,
        vm_primitive: str | None = None,
    ) -> list[SearchHit]:
        conditions: list[str] = []
        params: list[object] = []
        if source_class is not None:
            conditions.append("r.source_class = ?")
            params.append(source_class.value)
        if host_profile is not None:
            conditions.append("r.host_profile = ?")
            params.append(host_profile.value)
        if tag is not None:
            conditions.append(
                "instr(char(10) || r.tags || char(10), char(10) || ? || char(10)) > 0"
            )
            params.append(tag)
        if technique is not None:
            conditions.append(
                "instr(char(10) || r.techniques || char(10), char(10) || ? || char(10)) > 0"
            )
            params.append(technique)
        if vm_primitive is not None:
            conditions.append(
                "instr(char(10) || r.vm_primitives || char(10), char(10) || ? || char(10)) > 0"
            )
            params.append(vm_primitive)

        with self._connect() as db:
            if query.strip():
                where = ["records_fts MATCH ?", *conditions]
                rows = db.execute(
                    f"""
                    SELECT r.payload_json, bm25(records_fts)
                    FROM records_fts
                    JOIN records r ON r.id = records_fts.rowid
                    WHERE {' AND '.join(where)}
                    ORDER BY bm25(records_fts) ASC
                    """,
                    [query, *params],
                ).fetchall()
            else:
                where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
                rows = db.execute(
                    f"""
                    SELECT r.payload_json, 0.0
                    FROM records r
                    {where_sql}
                    ORDER BY r.name COLLATE NOCASE ASC
                    """,
                    params,
                ).fetchall()

        hits: list[SearchHit] = []
        for payload, score in rows:
            record = LiveProgRecord.model_validate_json(payload)
            hits.append(
                SearchHit(
                    record=record,
                    text_score=float(score),
                    authority_rank=record.source_class.rank,
                )
            )
        return sorted(
            hits,
            key=lambda hit: (hit.text_score, hit.authority_rank, hit.record.name.casefold()),
        )[:limit]
