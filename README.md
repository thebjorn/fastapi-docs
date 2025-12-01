![CI](https://github.com/thebjorn/fastapi-docs/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/github/thebjorn/fastapi-docs/graph/badge.svg?token=KSAWS3CH7A)](https://codecov.io/github/thebjorn/fastapi-docs)
[![pypi](https://img.shields.io/pypi/v/fastapi-docs?label=pypi%20fastapi-docs)](https://pypi.org/project/fastapi-docs/)
[![downloads](https://pepy.tech/badge/fastapi-docs)](https://pepy.tech/project/fastapi-docs)
[![Socket Badge](https://socket.dev/api/badge/pypi/package/fastapi-docs/0.1.7?artifact_id=tar-gz)](https://socket.dev/pypi/package/fastapi-docs/overview/0.1.7/tar-gz)

# fastapi-docs

A markdown documentation renderer for FastAPI applications.

## Features

- 📁 Directory-based navigation from your markdown file structure
- 🔍 Full-text search across all documents
- 🎨 Syntax highlighting for Python, JavaScript, bash, C#, HTML
- 🌙 Automatic dark mode based on system preference
- 📱 Responsive design for mobile and desktop
- ⚡ Hot-reload during development
- 📑 Table of contents for each page
- 🔗 Previous/next navigation

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_docs import create_docs_router, DocsConfig

app = FastAPI()

# Simple usage
app.include_router(create_docs_router("./userdocs"), prefix="/userdocs")

# Or with configuration
config = DocsConfig(
    docs_dir="./userdocs",
    title="My API Docs",
    auto_refresh=True,
)
app.include_router(create_docs_router(config), prefix="/userdocs")
```

## Markdown Frontmatter

Each markdown file can include YAML frontmatter:

```markdown
---
title: Getting Started
order: 1
description: Learn how to get started
tags:
  - quickstart
hidden: false
---

# Getting Started

Your content here...
```

## Running the Example

```bash
pip install -e ".[dev]"
uvicorn example_app:app --reload
```

Then visit http://localhost:8000/userdocs

## License

MIT
