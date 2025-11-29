"""Pydantic models for the documentation system."""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class DocMetadata(BaseModel):
    """Metadata extracted from document frontmatter.
    """

    title: str
    order: int = Field(default=999, description="Sort order within parent")
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    hidden: bool = Field(default=False, description="Exclude from navigation")


class TocEntry(BaseModel):
    """A table-of-contents entry extracted from headings.
    """

    text: str
    level: int
    slug: str


class NavItem(BaseModel):
    """Navigation tree item for JSON serialization.
    """

    title: str
    path: str
    children: list["NavItem"] = Field(default_factory=list)


class Breadcrumb(BaseModel):
    """Breadcrumb navigation item.
    """

    title: str
    path: str


class SearchResult(BaseModel):
    """Search result with context.
    """

    path: str
    title: str
    snippet: str
    score: float


class RenderResult(BaseModel):
    """Result of rendering a markdown document.
    """

    html: str
    toc: list[TocEntry] = Field(default_factory=list)


class DocNode(BaseModel):
    """A node in the documentation tree.
    """

    path: str
    source_path: Optional[Path] = None
    metadata: DocMetadata
    is_section: bool = False
    children: list["DocNode"] = Field(default_factory=list)
    raw_content: str = ""

    model_config = {"arbitrary_types_allowed": True}
