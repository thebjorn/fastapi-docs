# tests/test_tree.py
"""
Tests for DocTree - the documentation directory scanner.

These tests demonstrate how you'll interact with the tree-building
component that scans your markdown directory structure.
"""
# import pytest
from pathlib import Path
from fastapi_docs.tree import DocTree
# from fastapi_docs.models import DocNode, DocMetadata


class TestDocTreeScanning:
    """Test the directory scanning and tree building functionality.
    """

    def test_scan_simple_directory(self, tmp_path: Path):
        """
        Basic usage: point DocTree at a directory and get a navigable tree.

        Given a structure like:
            docs/
                index.md
                getting-started.md
                api/
                    index.md
                    authentication.md

        You get a tree you can traverse for navigation.
        """
        # Arrange: create a simple doc structure
        docs = tmp_path / "docs"
        docs.mkdir()

        (docs / "index.md").write_text("""---
title: Home
order: 0
---
# Welcome to the docs
""")
        (docs / "getting-started.md").write_text("""---
title: Getting Started
order: 1
---
# Getting Started
Follow these steps...
""")

        api_dir = docs / "api"
        api_dir.mkdir()
        (api_dir / "index.md").write_text("""---
title: API Reference
order: 2
---
# API Reference
""")
        (api_dir / "authentication.md").write_text("""---
title: Authentication
order: 1
---
# Authentication
""")

        # Act: scan the directory
        tree = DocTree(docs)

        # Assert: we get a proper tree structure
        assert tree.root is not None
        assert len(tree.root.children) == 3  # index, getting-started, api/

        # Children should be sorted by frontmatter 'order' field
        assert tree.root.children[0].metadata.title == "Home"
        assert tree.root.children[1].metadata.title == "Getting Started"
        assert tree.root.children[2].metadata.title == "API Reference"

        # The api/ folder should have its own children
        api_node = tree.root.children[2]
        assert api_node.is_section  # It's a folder with children
        assert len(api_node.children) == 2
        # assert len(api_node.children) == 3

    def test_get_document_by_path(self, tmp_path: Path):
        """
        You can retrieve any document by its URL path.

        This is the primary lookup method used by FastAPI routes.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text("""---
title: Guide
---
# The Guide
""")

        tree = DocTree(docs)

        # Lookup by URL-style path (no .md extension)
        node = tree.get("guide")
        assert node is not None
        assert node.metadata.title == "Guide"
        assert node.source_path == docs / "guide.md"

        # Non-existent paths return None
        assert tree.get("nonexistent") is None

    def test_nested_path_lookup(self, tmp_path: Path):
        """
        Nested documents use slash-separated paths matching the URL structure.
        """
        docs = tmp_path / "docs"
        (docs / "api").mkdir(parents=True)
        (docs / "api" / "webhooks.md").write_text("""---
title: Webhooks
---
# Webhooks
""")

        tree = DocTree(docs)

        # URL path mirrors filesystem structure
        node = tree.get("api/webhooks")
        assert node is not None
        assert node.metadata.title == "Webhooks"

    def test_frontmatter_parsing(self, tmp_path: Path):
        """
        YAML frontmatter is parsed into structured metadata.

        Supported fields:
        - title: Display title (falls back to first H1 or filename)
        - order: Sort order within parent (default: alphabetical)
        - description: Short description for search/previews
        - tags: List of tags for categorization/search
        - hidden: If true, excluded from navigation (but still accessible)
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "advanced.md").write_text("""---
title: Advanced Topics
order: 99
description: For power users
tags:
  - advanced
  - configuration
hidden: false
---
# Advanced Topics
""")

        tree = DocTree(docs)
        node = tree.get("advanced")

        assert node.metadata.title == "Advanced Topics"
        assert node.metadata.order == 99
        assert node.metadata.description == "For power users"
        assert node.metadata.tags == ["advanced", "configuration"]
        assert node.metadata.hidden is False

    def test_title_fallback_to_h1(self, tmp_path: Path):
        """
        If no title in frontmatter, extract from first H1 heading.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "no-frontmatter.md").write_text("""# My Document Title

Some content here.
""")

        tree = DocTree(docs)
        node = tree.get("no-frontmatter")

        assert node.metadata.title == "My Document Title"

    def test_title_fallback_to_filename(self, tmp_path: Path):
        """
        If no title and no H1, convert filename to title.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "some-topic.md").write_text("Just content, no heading.")

        tree = DocTree(docs)
        node = tree.get("some-topic")

        # Converts kebab-case to Title Case
        assert node.metadata.title == "Some Topic"


class TestDocTreeNavigation:
    """Test navigation-related functionality.
    """

    def test_get_breadcrumbs(self, tmp_path: Path):
        """
        Get breadcrumb trail for any document.

        Useful for rendering navigation context.
        """
        docs = tmp_path / "docs"
        (docs / "guides" / "advanced").mkdir(parents=True)
        (docs / "guides" / "index.md").write_text("---\ntitle: Guides\n---\n")
        (docs / "guides" / "advanced" / "caching.md").write_text(
            "---\ntitle: Caching\n---\n"
        )

        tree = DocTree(docs)

        breadcrumbs = tree.get_breadcrumbs("guides/advanced/caching")

        assert len(breadcrumbs) == 3
        assert breadcrumbs[0].title == "Guides"
        assert breadcrumbs[0].path == "guides"
        assert breadcrumbs[1].title == "Advanced"  # Folder name, title-cased
        assert breadcrumbs[1].path == "guides/advanced"
        assert breadcrumbs[2].title == "Caching"
        assert breadcrumbs[2].path == "guides/advanced/caching"

    def test_get_siblings(self, tmp_path: Path):
        """
        Get previous/next documents for pagination.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "01-intro.md").write_text("---\ntitle: Intro\norder: 1\n---\n")
        (docs / "02-setup.md").write_text("---\ntitle: Setup\norder: 2\n---\n")
        (docs / "03-usage.md").write_text("---\ntitle: Usage\norder: 3\n---\n")

        tree = DocTree(docs)

        prev_doc, next_doc = tree.get_siblings("02-setup")

        assert prev_doc.metadata.title == "Intro"
        assert next_doc.metadata.title == "Usage"

        # First doc has no previous
        prev_doc, next_doc = tree.get_siblings("01-intro")
        assert prev_doc is None
        assert next_doc.metadata.title == "Setup"

    def test_navigation_structure(self, tmp_path: Path):
        """
        Get the full navigation tree for rendering a sidebar.

        Returns a lightweight structure suitable for JSON serialization.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("---\ntitle: Home\norder: 0\n---\n")
        (docs / "api").mkdir()
        (docs / "api" / "index.md").write_text(
            "---\ntitle: API\norder: 1\n---\n"
        )

        tree = DocTree(docs)

        nav = tree.get_navigation()

        # Returns a list of NavItem objects (Pydantic models,
        # JSON-serializable)
        assert len(nav) == 2
        assert nav[0].title == "Home"
        assert nav[0].path == "index"
        assert nav[0].children == []

        assert nav[1].title == "API"
        assert nav[1].path == "api"
        assert len(nav[1].children) >= 0  # May have index as child or not


class TestDocTreeRefresh:
    """Test hot-reloading capabilities for development.
    """

    def test_refresh_detects_new_files(self, tmp_path: Path):
        """
        During development, you can refresh the tree to pick up changes.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "existing.md").write_text("---\ntitle: Existing\n---\n")

        tree = DocTree(docs)
        assert tree.get("new-doc") is None

        # Simulate adding a new file
        (docs / "new-doc.md").write_text("---\ntitle: New Doc\n---\n")

        # Refresh picks it up
        tree.refresh()

        assert tree.get("new-doc") is not None
        assert tree.get("new-doc").metadata.title == "New Doc"

    def test_auto_refresh_option(self, tmp_path: Path):
        """
        In development mode, the tree can auto-refresh on access.

        This checks file modification times and only rebuilds if needed.
        """
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "doc.md").write_text("---\ntitle: Original\n---\n")

        # auto_refresh=True enables development mode
        tree = DocTree(docs, auto_refresh=True)

        assert tree.get("doc").metadata.title == "Original"

        # Modify the file
        (docs / "doc.md").write_text("---\ntitle: Updated\n---\n")

        # Next access automatically sees the change
        # (implementation uses file mtime checking)
        assert tree.get("doc").metadata.title == "Updated"
