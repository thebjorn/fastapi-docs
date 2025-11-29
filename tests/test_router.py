# tests/test_router.py
"""
Tests for FastAPI router integration.

These tests demonstrate how to mount the documentation in your FastAPI app.
"""
import pytest
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_docs import create_docs_router, DocsConfig


class TestRouterSetup:
    """Test mounting and configuring the docs router."""

    def test_basic_mount(self, tmp_path: Path):
        """
        Simplest setup: point at a docs directory and mount the router.
        """
        # Create a minimal docs directory
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("""---
title: Home
---
# Welcome

This is the home page.
""")
        
        # Create router and mount it
        app = FastAPI()
        docs_router = create_docs_router(docs)
        app.include_router(docs_router, prefix="/docs")
        
        client = TestClient(app)
        
        # The index page is served
        response = client.get("/docs/")
        assert response.status_code == 200
        assert "Welcome" in response.text

    def test_custom_configuration(self, tmp_path: Path):
        """
        You can customize behavior through DocsConfig.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text("# Page")
        
        config = DocsConfig(
            docs_dir=docs,
            title="My API Docs",           # Site title
            logo_url="/static/logo.png",   # Logo for the header
            base_template="custom.html",   # Your own Jinja2 template
            syntax_theme="monokai",        # Pygments theme for code
            auto_refresh=True,             # Dev mode: watch for changes
        )
        
        app = FastAPI()
        docs_router = create_docs_router(config)
        app.include_router(docs_router, prefix="/docs")
        
        client = TestClient(app)
        response = client.get("/docs/page")
        assert response.status_code == 200


class TestDocumentRoutes:
    """Test document serving routes."""

    def test_serve_nested_document(self, tmp_path: Path):
        """
        Nested documents are served with path-style URLs.
        """
        docs = tmp_path / "docs"
        (docs / "api" / "v2").mkdir(parents=True)
        (docs / "api" / "v2" / "endpoints.md").write_text("""---
title: V2 Endpoints
---
# V2 API Endpoints
""")
        
        app = FastAPI()
        app.include_router(create_docs_router(docs), prefix="/docs")
        client = TestClient(app)
        
        response = client.get("/docs/api/v2/endpoints")
        assert response.status_code == 200
        assert "V2 API Endpoints" in response.text

    def test_index_shorthand(self, tmp_path: Path):
        """
        /section/ serves /section/index.md if it exists.
        """
        docs = tmp_path / "docs"
        (docs / "guides").mkdir(parents=True)
        (docs / "guides" / "index.md").write_text("# Guides Index")
        
        app = FastAPI()
        app.include_router(create_docs_router(docs), prefix="/docs")
        client = TestClient(app)
        
        # Both /guides and /guides/ serve the index
        response = client.get("/docs/guides")
        assert response.status_code == 200
        assert "Guides Index" in response.text

    def test_404_for_missing_document(self, tmp_path: Path):
        """
        Missing documents return 404 with a helpful page.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        
        app = FastAPI()
        app.include_router(create_docs_router(docs), prefix="/docs")
        client = TestClient(app)
        
        response = client.get("/docs/nonexistent")
        assert response.status_code == 404


class TestNavigationAPI:
    """Test the JSON API for navigation data."""

    def test_navigation_endpoint(self, tmp_path: Path):
        """
        GET /docs/_nav returns the navigation tree as JSON.
        
        Useful for building client-side navigation or SPAs.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "intro.md").write_text("---\ntitle: Introduction\norder: 1\n---\n")
        (docs / "setup.md").write_text("---\ntitle: Setup\norder: 2\n---\n")
        
        app = FastAPI()
        app.include_router(create_docs_router(docs), prefix="/docs")
        client = TestClient(app)
        
        response = client.get("/docs/_nav")
        assert response.status_code == 200
        
        nav = response.json()
        assert len(nav) == 2
        assert nav[0]["title"] == "Introduction"
        assert nav[0]["path"] == "intro"
        assert nav[1]["title"] == "Setup"

    def test_document_metadata_endpoint(self, tmp_path: Path):
        """
        GET /docs/_meta/{path} returns metadata for a specific document.
        
        Includes title, description, breadcrumbs, siblings, TOC.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text("""---
title: My Page
description: A page about things
---
# My Page

## Section One

## Section Two
""")
        
        app = FastAPI()
        app.include_router(create_docs_router(docs), prefix="/docs")
        client = TestClient(app)
        
        response = client.get("/docs/_meta/page")
        assert response.status_code == 200
        
        meta = response.json()
        assert meta["title"] == "My Page"
        assert meta["description"] == "A page about things"
        # assert len(meta["toc"]) == 3  # H1 + two H2s
        assert len(meta["toc"]) == 2  # H1 + two H2s


class TestSearchAPI:
    """Test the optional search functionality."""

    def test_search_endpoint(self, tmp_path: Path):
        """
        GET /docs/_search?q=query searches document content.
        
        Returns matching documents with highlighted snippets.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "auth.md").write_text("""---
title: Authentication
---
# Authentication

Use Bearer tokens for API authentication. Include the token in the Authorization header.
""")
        (docs / "intro.md").write_text("""---
title: Introduction
---
# Introduction

Welcome to the API documentation.
""")
        
        config = DocsConfig(docs_dir=docs, enable_search=True)
        
        app = FastAPI()
        app.include_router(create_docs_router(config), prefix="/docs")
        client = TestClient(app)
        
        response = client.get("/docs/_search?q=bearer+token")
        assert response.status_code == 200
        
        results = response.json()
        assert len(results) >= 1
        assert results[0]["path"] == "auth"
        assert "Bearer" in results[0]["snippet"] or "token" in results[0]["snippet"]

    def test_search_respects_hidden_documents(self, tmp_path: Path):
        """
        Hidden documents are excluded from search results.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "public.md").write_text("---\ntitle: Public\n---\nSearchable content.")
        (docs / "hidden.md").write_text("---\ntitle: Hidden\nhidden: true\n---\nSecret content.")
        
        config = DocsConfig(docs_dir=docs, enable_search=True)
        
        app = FastAPI()
        app.include_router(create_docs_router(config), prefix="/docs")
        client = TestClient(app)
        
        response = client.get("/docs/_search?q=content")
        results = response.json()
        
        paths = [r["path"] for r in results]
        assert "public" in paths
        assert "hidden" not in paths


class TestStaticAssets:
    """Test handling of static assets in the docs directory."""

    def test_serve_images(self, tmp_path: Path):
        """
        Images in the docs directory are served correctly.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text("# Page\n\n![Diagram](./diagram.png)")
        
        # Create a fake image
        (docs / "diagram.png").write_bytes(b"PNG FAKE DATA")
        
        app = FastAPI()
        app.include_router(create_docs_router(docs), prefix="/docs")
        client = TestClient(app)
        
        response = client.get("/docs/diagram.png")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/")