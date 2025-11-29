"""
Test that all modules are importable.
"""

import fastapi_docs
import fastapi_docs.config
import fastapi_docs.models
import fastapi_docs.renderer
import fastapi_docs.router
import fastapi_docs.search
import fastapi_docs.tree


def test_import_fastapi_docs():
    """Test that all modules are importable.
    """
    
    assert fastapi_docs
    assert fastapi_docs.config
    assert fastapi_docs.models
    assert fastapi_docs.renderer
    assert fastapi_docs.router
    assert fastapi_docs.search
    assert fastapi_docs.tree
