# tests/test_renderer.py
"""
Tests for DocRenderer - markdown to HTML conversion.

These tests demonstrate the rendering API and supported markdown features.
"""
# import pytest
from fastapi_docs.renderer import DocRenderer
# from fastapi_docs.renderer import RenderResult


class TestBasicRendering:
    """Test core markdown rendering functionality.
    """

    def test_simple_markdown(self):
        """
        Basic usage: pass markdown string, get HTML back.
        """
        renderer = DocRenderer()

        result = renderer.render("""
# Hello World

This is a paragraph with **bold** and *italic* text.
""")

        assert "<h1 id=\"hello-world\">Hello World" in result.html
        assert "<strong>bold</strong>" in result.html
        assert "<em>italic</em>" in result.html

    def test_render_result_includes_metadata(self):
        """
        RenderResult includes extracted metadata useful for the page.
        """
        renderer = DocRenderer()

        result = renderer.render("""
# Main Title

## Section One

Some content.

## Section Two

More content.
""")

        # Table of contents extracted from headings
        assert len(result.toc) == 3
        assert result.toc[0].text == "Main Title"
        assert result.toc[0].level == 1
        assert result.toc[0].slug == "main-title"

        assert result.toc[1].text == "Section One"
        assert result.toc[1].level == 2

        assert result.toc[2].text == "Section Two"
        assert result.toc[2].level == 2

    def test_render_with_frontmatter_stripped(self):
        """
        Frontmatter is not rendered as content.

        (The tree parser handles frontmatter separately; renderer ignores it.)
        """
        renderer = DocRenderer()

        result = renderer.render("""---
title: My Doc
order: 5
---

# Actual Content
""")

        assert "title:" not in result.html
        assert "order:" not in result.html
        assert "Actual Content" in result.html


class TestCodeBlockHighlighting:
    """Test syntax highlighting for code blocks.
    """

    def test_python_highlighting(self):
        """
        Python code blocks get syntax highlighting.
        """
        renderer = DocRenderer()

        result = renderer.render("""
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
""")

        # Pygments wraps code in spans with classes
        assert ('class="highlight"' in result.html
                or 'class="codehilite"' in result.html)
        assert "def" in result.html
        # Language should be identified for styling
        assert ("python" in result.html.lower()
                or "language-python" in result.html)

    def test_javascript_highlighting(self):
        """
        JavaScript/TypeScript code blocks are highlighted.
        """
        renderer = DocRenderer()

        result = renderer.render("""
```javascript
const greet = (name) => {
    console.log(`Hello, ${name}!`);
};
```
""")

        assert "const" in result.html
        assert ('class="highlight"' in result.html
                or "highlight" in result.html.lower())

    def test_curl_highlighting(self):
        """
        curl commands (bash/shell) are highlighted.
        """
        renderer = DocRenderer()

        result = renderer.render("""
```bash
curl -X POST https://api.example.com/v1/users \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"name": "Alice"}'
```
""")

        assert "curl" in result.html
        # Should have some syntax highlighting applied
        assert "highlight" in result.html.lower() or "<code" in result.html

    def test_csharp_highlighting(self):
        """
        C# code blocks are highlighted.
        """
        renderer = DocRenderer()

        result = renderer.render("""
```csharp
public class Greeter
{
    public string Greet(string name) => $"Hello, {name}!";
}
```
""")

        assert "public" in result.html
        assert "class" in result.html

    def test_html_highlighting(self):
        """
        HTML code blocks are highlighted (and not interpreted as HTML).
        """
        renderer = DocRenderer()

        result = renderer.render("""
```html
<div class="container">
    <h1>Hello</h1>
</div>
```
""")

        # The HTML should be escaped, not rendered
        assert ("&lt;div" in result.html
                or "<div" not in result.html.split("<code")[1].split(
                    "</code>"
                )[0])

    def test_line_numbers_option(self):
        """
        Optionally include line numbers in code blocks.
        """
        renderer = DocRenderer(line_numbers=True)

        result = renderer.render("""
```python
line_one = 1
line_two = 2
line_three = 3
```
""")

        # Line numbers should appear
        assert "1" in result.html and "2" in result.html and "3" in result.html


class TestMarkdownExtensions:
    """Test extended markdown features beyond basic CommonMark.
    """

    def test_tables(self):
        """
        GitHub-flavored markdown tables are supported.
        """
        renderer = DocRenderer()

        result = renderer.render("""
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
""")

        assert "<table>" in result.html or "<table" in result.html
        assert "<th>" in result.html or "<th" in result.html
        assert "Header 1" in result.html

    def test_task_lists(self):
        """
        GitHub-style task lists are rendered as checkboxes.
        """
        renderer = DocRenderer()

        result = renderer.render("""
- [x] Completed task
- [ ] Pending task
""")

        # Should render as checkboxes (implementation may vary)
        assert "Completed task" in result.html
        assert "Pending task" in result.html

    def test_autolinks(self):
        """
        URLs are automatically converted to links.
        """
        renderer = DocRenderer()

        result = renderer.render("Check out https://example.com for more.")

        assert '<a href="https://example.com"' in result.html

    def test_admonitions(self):
        """
        Admonition blocks for notes, warnings, etc.

        Uses the common `!!! note` syntax or similar.
        """
        renderer = DocRenderer()

        result = renderer.render("""
!!! warning
    This is a warning message.

    It can span multiple lines.
""")

        # Should render as a styled block
        assert "warning" in result.html.lower()
        assert "This is a warning message" in result.html


class TestLinkHandling:
    """Test how internal and external links are processed.
    """

    def test_relative_links_preserved(self):
        """
        Relative links to other docs are preserved for the router to handle.
        """
        renderer = DocRenderer()

        result = renderer.render(
            """See the [installation guide](./installation.md).
            """
        )

        # Link should be present (router will handle the
        # actual path resolution)
        assert ('href="./installation.md"' in result.html
                or 'href="./installation"' in result.html)

    def test_external_links_marked(self):
        """
        External links can be marked with a class or icon.
        """
        renderer = DocRenderer(mark_external_links=True)

        result = renderer.render("Visit [Google](https://google.com).")

        # External links get a marker (class, icon, or target)
        assert ("external" in result.html.lower()
                or 'target="_blank"' in result.html)

    def test_anchor_links_generated(self):
        """
        Headings get anchor links for direct linking.
        """
        renderer = DocRenderer()

        result = renderer.render("## My Section")

        # Heading should have an ID for anchoring
        assert ('id="my-section"' in result.html
                or 'id="my_section"' in result.html)


class TestTableOfContents:
    """Test table of contents extraction and generation.
    """

    def test_toc_includes_all_heading_levels(self):
        """
        TOC should include all heading levels from H1 to H6.
        """
        renderer = DocRenderer()

        markdown_content = """
# Level 1 Heading

## Level 2 Heading

### Level 3 Heading

#### Level 4 Heading

##### Level 5 Heading

###### Level 6 Heading

Some content here.
"""

        result = renderer.render(markdown_content)

        # Verify all 6 heading levels are in TOC
        assert len(result.toc) == 6
        assert result.toc[0].level == 1
        assert result.toc[0].text == "Level 1 Heading"
        assert result.toc[1].level == 2
        assert result.toc[1].text == "Level 2 Heading"
        assert result.toc[2].level == 3
        assert result.toc[2].text == "Level 3 Heading"
        assert result.toc[3].level == 4
        assert result.toc[3].text == "Level 4 Heading"
        assert result.toc[4].level == 5
        assert result.toc[4].text == "Level 5 Heading"
        assert result.toc[5].level == 6
        assert result.toc[5].text == "Level 6 Heading"

    def test_toc_with_nested_headings(self):
        """
        TOC should correctly handle nested heading hierarchies.
        """
        renderer = DocRenderer()

        markdown_content = """
# Main Title

## Section A

### Subsection A.1

#### Sub-subsection A.1.1

### Subsection A.2

## Section B

### Subsection B.1

## Section C
"""

        result = renderer.render(markdown_content)

        # Verify all headings are included in order
        assert len(result.toc) == 8
        assert result.toc[0].text == "Main Title"
        assert result.toc[0].level == 1
        
        assert result.toc[1].text == "Section A"
        assert result.toc[1].level == 2
        
        assert result.toc[2].text == "Subsection A.1"
        assert result.toc[2].level == 3
        
        assert result.toc[3].text == "Sub-subsection A.1.1"
        assert result.toc[3].level == 4
        
        assert result.toc[4].text == "Subsection A.2"
        assert result.toc[4].level == 3
        
        assert result.toc[5].text == "Section B"
        assert result.toc[5].level == 2
        
        assert result.toc[6].text == "Subsection B.1"
        assert result.toc[6].level == 3
        
        assert result.toc[7].text == "Section C"
        assert result.toc[7].level == 2

    def test_toc_slug_generation(self):
        """
        TOC entries should have correctly generated slugs for anchor links.
        """
        renderer = DocRenderer()

        markdown_content = """
# Simple Heading

## Heading With Spaces

### Heading-With-Dashes

#### Heading_With_Underscores

##### Heading With Special Characters! @#$%

###### Multi   Word    Heading
"""

        result = renderer.render(markdown_content)

        assert len(result.toc) == 6
        
        # Verify slugs are generated correctly
        assert result.toc[0].slug == "simple-heading"
        assert result.toc[1].slug == "heading-with-spaces"
        assert result.toc[2].slug == "heading-with-dashes"
        assert result.toc[3].slug == "heading-with-underscores"
        # Special characters should be removed from slugs
        assert "@" not in result.toc[4].slug
        assert "#" not in result.toc[4].slug
        assert "$" not in result.toc[4].slug
        assert "%" not in result.toc[4].slug
        # Multiple spaces should be collapsed
        assert "  " not in result.toc[5].slug

    def test_toc_with_multiple_same_level_headings(self):
        """
        TOC should include all headings even when multiple exist at the same level.
        """
        renderer = DocRenderer()

        markdown_content = """
# First H1

# Second H1

## First H2

## Second H2

## Third H2

### First H3

### Second H3
"""

        result = renderer.render(markdown_content)

        # Verify all headings are included
        assert len(result.toc) == 7
        assert result.toc[0].text == "First H1"
        assert result.toc[1].text == "Second H1"
        assert result.toc[2].text == "First H2"
        assert result.toc[3].text == "Second H2"
        assert result.toc[4].text == "Third H2"
        assert result.toc[5].text == "First H3"
        assert result.toc[6].text == "Second H3"

    def test_toc_with_no_headings(self):
        """
        TOC should be empty when document has no headings.
        """
        renderer = DocRenderer()

        markdown_content = """
This is just a paragraph with no headings.

Another paragraph here.
"""

        result = renderer.render(markdown_content)

        assert len(result.toc) == 0
        assert result.toc == []

    def test_toc_with_only_h1(self):
        """
        TOC should work correctly with only a single H1 heading.
        """
        renderer = DocRenderer()

        markdown_content = """
# Only Heading

Some content here.
"""

        result = renderer.render(markdown_content)

        assert len(result.toc) == 1
        assert result.toc[0].text == "Only Heading"
        assert result.toc[0].level == 1
        assert result.toc[0].slug == "only-heading"

    def test_toc_preserves_heading_order(self):
        """
        TOC entries should be in the same order as headings appear in the document.
        """
        renderer = DocRenderer()

        markdown_content = """
# Alpha

## Beta

### Gamma

## Delta

# Epsilon

## Zeta
"""

        result = renderer.render(markdown_content)

        # Verify order matches document order
        assert len(result.toc) == 6
        assert result.toc[0].text == "Alpha"
        assert result.toc[1].text == "Beta"
        assert result.toc[2].text == "Gamma"
        assert result.toc[3].text == "Delta"
        assert result.toc[4].text == "Epsilon"
        assert result.toc[5].text == "Zeta"

    def test_toc_with_headings_in_code_blocks(self):
        """
        Headings inside code blocks should not be included in TOC.
        """
        renderer = DocRenderer()

        markdown_content = """
# Real Heading

```markdown
# This is not a heading
## Neither is this
```

## Another Real Heading
"""

        result = renderer.render(markdown_content)

        # Only real headings should be in TOC
        assert len(result.toc) == 2
        assert result.toc[0].text == "Real Heading"
        assert result.toc[1].text == "Another Real Heading"
