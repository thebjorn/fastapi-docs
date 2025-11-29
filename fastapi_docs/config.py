"""Configuration for the documentation system."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union


@dataclass
class DocsConfig:
    """
    Configuration for the documentation router.

    Attributes:
        docs_dir: Path to the directory containing markdown files.
        title: Site title displayed in the header.
        description: Site description for meta tags.
        logo_url: URL to logo image (displayed in header).
        favicon_url: URL to favicon.
        copyright_text: Copyright notice for the footer.
        footer_links: Additional links for the footer as (text, url) tuples.
        syntax_theme: Pygments theme for code highlighting.
        auto_refresh: If True, watch for file changes (development mode).
        enable_search: If True, enable the search endpoint.
        base_template: Path to custom Jinja2 base template.
        extra_css: Additional CSS to inject into pages.
        extra_js: Additional JavaScript to inject into pages.
        line_numbers: If True, show line numbers in code blocks.
        mark_external_links: If True, mark external links with an icon.
    """

    docs_dir: Union[str, Path]
    title: str = "Documentation"
    description: str = ""
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    copyright_text: str = ""
    footer_links: list[tuple[str, str]] = field(default_factory=list)
    syntax_theme: str = "default"
    auto_refresh: bool = False
    enable_search: bool = True
    base_template: Optional[str] = None
    extra_css: str = ""
    extra_js: str = ""
    line_numbers: bool = False
    mark_external_links: bool = True

    def __post_init__(self):
        if isinstance(self.docs_dir, str):
            self.docs_dir = Path(self.docs_dir)
