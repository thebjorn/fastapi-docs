"""Behavioral coverage for search, refresh, and optional router features."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_docs import DocsConfig, create_docs_router
from fastapi_docs.models import DocMetadata, DocNode
from fastapi_docs.search import SearchIndex
from fastapi_docs.tree import DocTree


def _document(path: str, title: str, content: str,
              description: str | None = None) -> DocNode:
    """Create an in-memory document for search tests."""
    return DocNode(
        path=path,
        metadata=DocMetadata(title=title, description=description),
        raw_content=content,
    )


def test_search_scoring_limits_and_snippets():
    """Search scores all indexed fields and returns bounded context."""
    index = SearchIndex()
    index.index_all([
        _document(
            'python',
            'Python',
            ('prefix ' * 30) + ('python ' * 8) + ('suffix ' * 30),
            'Python language guide',
        ),
        _document('guide', 'Other Guide', 'A short Python example.'),
        _document('unrelated', 'Unrelated', 'No matching terms.'),
    ])

    assert index.search('   ') == []
    results = index.search('python', limit=1)

    assert [result.path for result in results] == ['python']
    assert results[0].score == 25.0
    assert results[0].snippet.startswith('...')
    assert results[0].snippet.endswith('...')


def test_search_snippet_without_a_match_starts_at_content_beginning():
    """Snippet generation has a useful fallback for absent query words."""
    index = SearchIndex()

    snippet = index._generate_snippet(
        'first second third fourth',
        ['absent'],
        context_chars=12,
    )

    assert snippet == 'first second...'


def test_missing_tree_and_hidden_navigation(tmp_path: Path):
    """Missing trees are empty and hidden pages remain directly accessible."""
    missing = DocTree(tmp_path / 'missing')

    assert missing.root is None
    assert missing.get_navigation() == []
    assert missing.get_siblings('anything') == (None, None)

    docs = tmp_path / 'docs'
    docs.mkdir()
    (docs / 'visible.md').write_text('# Visible')
    (docs / 'hidden.md').write_text(
        '---\ntitle: Hidden\nhidden: true\n---\nSecret'
    )
    (docs / 'notes.txt').write_text('not documentation')
    hidden_dir = docs / '_drafts'
    hidden_dir.mkdir()
    (hidden_dir / 'draft.md').write_text('# Draft')

    tree = DocTree(docs)

    assert tree.get('hidden') is not None
    assert [item.path for item in tree.get_navigation()] == ['visible']
    assert [node.path for node in tree.get_all_documents()] == ['visible']


def test_auto_refresh_detects_changed_and_deleted_files(tmp_path: Path):
    """Auto-refresh rebuilds its index for modifications and deletions."""
    docs = tmp_path / 'docs'
    docs.mkdir()
    page = docs / 'page.md'
    page.write_text('# Original')
    tree = DocTree(docs, auto_refresh=True)

    original_mtime = page.stat().st_mtime
    page.write_text('# Updated')
    os.utime(page, (original_mtime + 2, original_mtime + 2))
    assert tree.get('page').metadata.title == 'Updated'

    page.unlink()
    assert tree.get('page') is None
    assert tree.root is not None


def test_disabled_search_and_refresh_endpoint(tmp_path: Path):
    """Optional search can be disabled while manual refresh remains usable."""
    docs = tmp_path / 'docs'
    docs.mkdir()
    (docs / 'index.md').write_text('# Home')
    config = DocsConfig(docs_dir=docs, enable_search=False)
    app = FastAPI()
    app.include_router(create_docs_router(config), prefix='/docs')
    client = TestClient(app)

    assert client.get('/docs/_search?q=home').status_code == 404
    assert client.get('/docs/_refresh').json() == {'status': 'refreshed'}
    assert client.get('/docs/_meta/missing').status_code == 404


def test_config_converts_string_directory(tmp_path: Path):
    """String paths are normalized without changing existing Path values."""
    assert DocsConfig(str(tmp_path)).docs_dir == tmp_path
    assert DocsConfig(tmp_path).docs_dir is tmp_path
