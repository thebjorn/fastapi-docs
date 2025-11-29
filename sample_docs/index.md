---
title: Home
order: 0
description: Welcome to the documentation
---

# Welcome to the Documentation

This is a sample documentation site built with **fastapi-docs**. It demonstrates the key features of the markdown documentation system.

## Features

This documentation system supports:

- **Automatic navigation** - Your directory structure becomes the sidebar
- **Full-text search** - Find content across all documents
- **Syntax highlighting** - Beautiful code blocks for multiple languages
- **Dark mode** - Automatic detection based on system preference
- **Responsive design** - Works on desktop and mobile

## Quick Example

Here's a Python code example with syntax highlighting:

```python
from fastapi import FastAPI
from fastapi_docs import create_docs_router, DocsConfig

app = FastAPI()

config = DocsConfig(
    docs_dir="./docs",
    title="My API Documentation",
    auto_refresh=True,
)

app.include_router(create_docs_router(config), prefix="/userdocs")
```

## Getting Started

Check out the [API Reference](api) section to see more examples including:

- Authentication with Bearer tokens
- Making requests with curl
- Response handling in multiple languages

!!! tip
    Use `auto_refresh=True` during development to see changes immediately without restarting the server.
