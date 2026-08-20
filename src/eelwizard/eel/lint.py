import re

from eelwizard.corpus.liveprog import CONTROL_RE, parse_liveprog
from eelwizard.models import Diagnostic, DiagnosticSeverity, HostProfile

_STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"')


def _code_without_comment_or_string(line: str) -> str:
    code = line.split("//", 1)[0]
    return _STRING_RE.sub("", code)


def _looks_like_unterminated_assignment(stripped: str) -> bool:
    if not stripped or stripped.startswith(("//", "/*", "*", "@")):
        return False
    if CONTROL_RE.fullmatch(stripped):
        return False
    if any(operator in stripped for operator in ("==", "!=", "<=", ">=")):
        return False
    if "=" not in stripped or "?" in stripped:
        return False
    return not stripped.endswith((";", "(", ")", ":"))


def lint_liveprog(text: str, profile: HostProfile) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    document = parse_liveprog(text)
    if "init" not in document.sections:
        diagnostics.append(
            Diagnostic(
                code="HOST001",
                severity=DiagnosticSeverity.ERROR,
                message="missing @init",
            )
        )
    if "sample" not in document.sections:
        diagnostics.append(
            Diagnostic(
                code="HOST002",
                severity=DiagnosticSeverity.ERROR,
                message="missing @sample",
            )
        )
    if profile is HostProfile.ROOTLESS_UPSTREAM:
        for section in ("slider", "block"):
            if section in document.sections:
                diagnostics.append(
                    Diagnostic(
                        code="HOST003",
                        severity=DiagnosticSeverity.WARNING,
                        message=f"@{section} is not established as upstream-host truth in M0",
                    )
                )

    in_section = False
    for line_number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("@"):
            in_section = True
            continue
        if not in_section:
            continue
        code = _code_without_comment_or_string(raw)
        if "{" in code or "}" in code:
            diagnostics.append(
                Diagnostic(
                    code="EEL010",
                    severity=DiagnosticSeverity.ERROR,
                    message="C-style braces are invalid for core EEL control blocks",
                    line=line_number,
                )
            )
        if _looks_like_unterminated_assignment(stripped):
            diagnostics.append(
                Diagnostic(
                    code="EEL001",
                    severity=DiagnosticSeverity.ERROR,
                    message="assignment-like statement is missing semicolon",
                    line=line_number,
                )
            )
    return diagnostics
