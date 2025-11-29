"""DocTree: Directory scanner and navigation structure builder."""

import re
import time
from pathlib import Path
from typing import Optional
import frontmatter

from .models import DocNode, DocMetadata, NavItem, Breadcrumb


class DocTree:
    """Scans a documentation directory and builds a navigable tree structure."""
    
    def __init__(self, docs_dir: Path, auto_refresh: bool = False):
        self.docs_dir = Path(docs_dir)
        self.auto_refresh = auto_refresh
        self._root: Optional[DocNode] = None
        self._path_index: dict[str, DocNode] = {}
        self._last_scan_time: float = 0
        self._file_mtimes: dict[Path, float] = {}
        self._scan()
    
    @property
    def root(self) -> Optional[DocNode]:
        if self.auto_refresh:
            self._check_refresh()
        return self._root
    
    def get(self, path: str) -> Optional[DocNode]:
        """Retrieve a document by its URL path."""
        if self.auto_refresh:
            self._check_refresh()
        path = path.strip("/")
        index_path = f"{path}/index" if path else "index"
        # Prefer index documents for directory paths
        if index_path in self._path_index:
            return self._path_index[index_path]
        if path in self._path_index:
            return self._path_index[path]
        return None
    
    def get_breadcrumbs(self, path: str) -> list[Breadcrumb]:
        """Get the breadcrumb trail for a document path."""
        if self.auto_refresh:
            self._check_refresh()
        path = path.strip("/")
        parts = path.split("/") if path else []
        breadcrumbs = []
        current_path = ""
        for part in parts:
            current_path = f"{current_path}/{part}".strip("/")
            node = self._path_index.get(current_path)
            if node:
                breadcrumbs.append(Breadcrumb(title=node.metadata.title, path=current_path))
            else:
                breadcrumbs.append(Breadcrumb(title=self._filename_to_title(part), path=current_path))
        return breadcrumbs
    
    def get_siblings(self, path: str) -> tuple[Optional[DocNode], Optional[DocNode]]:
        """Get the previous and next documents relative to the given path."""
        if self.auto_refresh:
            self._check_refresh()
        flat_list = self._flatten_tree(self._root)
        path = path.strip("/")
        current_index = None
        for i, node in enumerate(flat_list):
            if node.path == path:
                current_index = i
                break
        if current_index is None:
            return None, None
        prev_node = flat_list[current_index - 1] if current_index > 0 else None
        next_node = flat_list[current_index + 1] if current_index < len(flat_list) - 1 else None
        return prev_node, next_node
    
    def get_navigation(self) -> list[NavItem]:
        """Get the navigation tree as a list of NavItem objects."""
        if self.auto_refresh:
            self._check_refresh()
        if not self._root:
            return []
        return self._build_nav_items(self._root.children)
    
    def refresh(self) -> None:
        """Force a rescan of the documentation directory."""
        self._scan()
    
    def get_all_documents(self) -> list[DocNode]:
        """Get a flat list of all documents (for search indexing)."""
        if self.auto_refresh:
            self._check_refresh()
        return [node for node in self._path_index.values() 
                if not node.is_section and not node.metadata.hidden]
    
    def _scan(self) -> None:
        self._last_scan_time = time.time()
        self._path_index.clear()
        self._file_mtimes.clear()
        if not self.docs_dir.exists():
            self._root = None
            return
        self._root = self._scan_directory(self.docs_dir, "")
    
    def _scan_directory(self, dir_path: Path, url_path: str) -> DocNode:
        children: list[DocNode] = []
        index_node: Optional[DocNode] = None
        items = sorted(dir_path.iterdir())
        
        for item in items:
            if item.is_file() and item.suffix == ".md":
                node = self._parse_markdown_file(item, url_path)
                self._file_mtimes[item] = item.stat().st_mtime
                if item.stem == "index":
                    index_node = node
                else:
                    children.append(node)
                    self._path_index[node.path] = node
            elif item.is_dir() and not item.name.startswith((".", "_")):
                child_url_path = f"{url_path}/{item.name}".strip("/")
                child_node = self._scan_directory(item, child_url_path)
                child_node.is_section = True
                children.append(child_node)
        
        # If an index exists, expose it as a child for navigation
        if index_node:
            self._path_index[index_node.path] = index_node
            children.insert(0, index_node)
        
        children.sort(key=lambda n: (n.metadata.order, n.metadata.title.lower()))
        
        # Always create a directory node representing this folder
        if index_node:
            dir_title = index_node.metadata.title
            dir_order = index_node.metadata.order
        else:
            dir_title = self._filename_to_title(dir_path.name if url_path else "root")
            dir_order = 999
        dir_node = DocNode(
            path=url_path,
            source_path=None,
            metadata=DocMetadata(title=dir_title, order=dir_order),
            is_section=True,
            children=children
        )
        if url_path:
            self._path_index[url_path] = dir_node
        return dir_node
    
    def _parse_markdown_file(self, file_path: Path, url_prefix: str) -> DocNode:
        post = frontmatter.load(file_path)
        content = post.content
        fm = post.metadata
        stem = file_path.stem
        url_path = (f"{url_prefix}/index" if stem == "index" else f"{url_prefix}/{stem}").strip("/")
        title = fm.get("title") or self._extract_h1(content) or self._filename_to_title(stem)
        metadata = DocMetadata(
            title=title,
            order=fm.get("order", 999),
            description=fm.get("description"),
            tags=fm.get("tags", []),
            hidden=fm.get("hidden", False)
        )
        return DocNode(path=url_path, source_path=file_path, metadata=metadata, 
                       is_section=False, children=[], raw_content=content)
    
    def _extract_h1(self, content: str) -> Optional[str]:
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1).strip() if match else None
    
    def _filename_to_title(self, filename: str) -> str:
        name = re.sub(r"^\d+[-_]", "", filename)
        name = re.sub(r"[-_]", " ", name)
        return name.title()
    
    def _build_nav_items(self, nodes: list[DocNode]) -> list[NavItem]:
        items = []
        for node in nodes:
            if node.metadata.hidden:
                continue
            path_for_nav = "index" if node.path == "" else node.path
            items.append(NavItem(title=node.metadata.title, path=path_for_nav,
                                children=self._build_nav_items(node.children)))
        return items
    
    def _flatten_tree(self, node: Optional[DocNode]) -> list[DocNode]:
        if node is None:
            return []
        result = []
        if node.source_path and not node.metadata.hidden:
            result.append(node)
        for child in node.children:
            result.extend(self._flatten_tree(child))
        return result
    
    def _check_refresh(self) -> None:
        if not self.auto_refresh:
            return
        needs_refresh = False
        for file_path, mtime in self._file_mtimes.items():
            if file_path.exists():
                if file_path.stat().st_mtime > mtime:
                    needs_refresh = True
                    break
            else:
                needs_refresh = True
                break
        if not needs_refresh and self.docs_dir.exists():
            if self.docs_dir.stat().st_mtime > self._last_scan_time:
                needs_refresh = True
        if needs_refresh:
            self._scan()
