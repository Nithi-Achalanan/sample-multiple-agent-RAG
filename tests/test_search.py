from src.tools.multiple_keyword_search import multiple_keyword_search


def test_search_matches_multiple_keywords(tmp_path):
    knowledge_base = tmp_path / "knowledge_base.txt"
    knowledge_base.write_text("RAG retrieves context.\nUnrelated sentence.", encoding="utf-8")

    assert multiple_keyword_search("retrieves context", knowledge_base) == ["RAG retrieves context."]

