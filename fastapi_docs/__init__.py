"""
fastapi-docs: A markdown documentation renderer for FastAPI.

Usage:
    from fastapi import FastAPI
    from fastapi_docs import create_docs_router, DocsConfig

    app = FastAPI()
    app.include_router(create_docs_router("./docs"), prefix="/docs")
"""

from .config import DocsConfig
from .router import create_docs_router
from .tree import DocTree
from .renderer import DocRenderer
from .models import DocNode, DocMetadata, NavItem, RenderResult, TocEntry

__all__ = [
    "create_docs_router",
    "DocsConfig",
    "DocTree",
    "DocRenderer",
    "DocNode",
    "DocMetadata",
    "NavItem",
    "RenderResult",
    "TocEntry",
]

__version__ = "0.1.6"
