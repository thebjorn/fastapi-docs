"""FastAPI router for serving documentation."""

from pathlib import Path
from typing import Optional, Union

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from jinja2 import Environment, PackageLoader, select_autoescape

from .config import DocsConfig
from .tree import DocTree
from .renderer import DocRenderer
from .search import SearchIndex


def create_docs_router(config_or_path: Union[DocsConfig, str, Path]) -> APIRouter:
    """Create a FastAPI router for serving documentation."""
    
    if isinstance(config_or_path, (str, Path)):
        config = DocsConfig(docs_dir=config_or_path)
    else:
        config = config_or_path
    
    tree = DocTree(config.docs_dir, auto_refresh=config.auto_refresh)
    renderer = DocRenderer(
        line_numbers=config.line_numbers,
        syntax_theme=config.syntax_theme,
        mark_external_links=config.mark_external_links,
    )
    
    search_index: Optional[SearchIndex] = None
    if config.enable_search:
        search_index = SearchIndex()
        search_index.index_all(tree.get_all_documents())
    
    jinja_env = Environment(
        loader=PackageLoader("fastapi_docs", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    jinja_env.globals["config"] = config
    jinja_env.globals["syntax_css"] = renderer.get_css()
    
    router = APIRouter()
    
    @router.get("/_nav", response_class=JSONResponse)
    async def get_navigation():
        nav = tree.get_navigation()
        return [item.model_dump() for item in nav]
    
    @router.get("/_meta/{path:path}", response_class=JSONResponse)
    async def get_document_metadata(path: str):
        node = tree.get(path)
        if not node:
            raise HTTPException(status_code=404, detail="Document not found 1")
        result = renderer.render(node.raw_content)
        breadcrumbs = tree.get_breadcrumbs(path)
        prev_node, next_node = tree.get_siblings(path)
        return {
            "title": node.metadata.title,
            "description": node.metadata.description,
            "tags": node.metadata.tags,
            "toc": [entry.model_dump() for entry in result.toc],
            "breadcrumbs": [bc.model_dump() for bc in breadcrumbs],
            "prev": {"title": prev_node.metadata.title, "path": prev_node.path} if prev_node else None,
            "next": {"title": next_node.metadata.title, "path": next_node.path} if next_node else None,
        }
    
    @router.get("/_search", response_class=JSONResponse)
    async def search_documents(q: str = ""):
        if not config.enable_search or search_index is None:
            raise HTTPException(status_code=404, detail="Search not enabled")
        if config.auto_refresh:
            search_index.index_all(tree.get_all_documents())
        results = search_index.search(q)
        return [result.model_dump() for result in results]
    
    @router.get("/_refresh", response_class=JSONResponse)
    async def refresh_tree():
        tree.refresh()
        if search_index:
            search_index.index_all(tree.get_all_documents())
        return {"status": "refreshed"}
    
    @router.get("/{path:path}", response_class=HTMLResponse)
    async def serve_document(request: Request, path: str = ""):
        if path:
            asset_path = config.docs_dir / path
            if asset_path.is_file() and asset_path.suffix != ".md":
                return FileResponse(asset_path)
        
        path = path.rstrip("/")
        # if not path:
        #     path = "index"
        
        node = tree.get(path)
        if not node:
            print("Not found: ", path)
            print("Tree: ", tree.root)
            raise HTTPException(status_code=404, detail="Document not found 2")
        
        result = renderer.render(node.raw_content)
        nav = tree.get_navigation()
        breadcrumbs = tree.get_breadcrumbs(path)
        prev_node, next_node = tree.get_siblings(path)
        
        template = jinja_env.get_template("document.html")
        # Compute base prefix for building absolute links within the mounted router
        mount_prefix = request.url.path[:-len(path)] if path else request.url.path
        if not mount_prefix.endswith("/"):
            mount_prefix = mount_prefix + "/"
        html = template.render(
            request=request,
            title=node.metadata.title,
            description=node.metadata.description,
            content=result.html,
            toc=result.toc,
            nav=nav,
            breadcrumbs=breadcrumbs,
            prev_doc=prev_node,
            next_doc=next_node,
            current_path=path,
            base_prefix=mount_prefix,
        )
        return HTMLResponse(content=html)
    
    return router
