from pathlib import Path


def multiple_keyword_search(query: str, knowledge_base: str | Path = "knowledge_base.txt") -> list[str]:
    """Return knowledge-base lines matching any query keyword."""
    keywords = {word.casefold() for word in query.split() if word.strip()}
    if not keywords:
        return []

    lines = Path(knowledge_base).read_text(encoding="utf-8").splitlines()
    return [line for line in lines if any(keyword in line.casefold() for keyword in keywords)]

