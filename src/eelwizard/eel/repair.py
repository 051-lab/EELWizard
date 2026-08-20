from eelwizard.models import Diagnostic


def apply_safe_repairs(text: str, diagnostics: list[Diagnostic]) -> str:
    targets = {
        diagnostic.line
        for diagnostic in diagnostics
        if diagnostic.code == "EEL001" and diagnostic.line is not None
    }
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines, start=1):
        if index not in targets:
            continue
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        body = line[: -len(ending)] if ending else line
        lines[index - 1] = body + ";" + ending
    return "".join(lines)
