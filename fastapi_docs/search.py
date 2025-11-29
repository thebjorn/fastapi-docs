"""Simple full-text search for documentation."""

import re
from dataclasses import dataclass, field
from typing import Optional

from .models import DocNode, SearchResult


@dataclass
class SearchIndex:
    """Simple in-memory search index for documentation."""
    
    _documents: dict[str, tuple[str, str, Optional[str]]] = field(default_factory=dict)
    
    def index_document(self, node: DocNode) -> None:
        self._documents[node.path] = (node.metadata.title, node.raw_content, 
                                       node.metadata.description)
    
    def index_all(self, documents: list[DocNode]) -> None:
        self._documents.clear()
        for doc in documents:
            self.index_document(doc)
    
    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search for documents matching the query."""
        if not query.strip():
            return []
        query_lower = query.lower()
        query_words = query_lower.split()
        results = []
        
        for path, (title, content, description) in self._documents.items():
            score = 0.0
            title_lower = title.lower()
            content_lower = content.lower()
            desc_lower = (description or "").lower()
            
            for word in query_words:
                if word in title_lower:
                    score += 10.0
                    if word == title_lower:
                        score += 5.0
                if word in desc_lower:
                    score += 5.0
                content_matches = content_lower.count(word)
                if content_matches > 0:
                    score += min(content_matches, 5) * 1.0
            
            if score > 0:
                snippet = self._generate_snippet(content, query_words)
                results.append(SearchResult(path=path, title=title, 
                                           snippet=snippet, score=score))
        
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]
    
    def _generate_snippet(self, content: str, query_words: list[str], 
                         context_chars: int = 150) -> str:
        content_lower = content.lower()
        best_pos = len(content)
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1 and pos < best_pos:
                best_pos = pos
        if best_pos == len(content):
            best_pos = 0
        start = max(0, best_pos - context_chars // 2)
        end = min(len(content), best_pos + context_chars)
        snippet = content[start:end]
        snippet = re.sub(r"\s+", " ", snippet).strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        return snippet
