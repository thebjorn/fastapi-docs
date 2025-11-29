"""
Example FastAPI application with documentation.

Run with: uvicorn example_app:app --reload
Then visit: http://localhost:8000/docs/
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_docs import create_docs_router, DocsConfig

# Create the FastAPI application
app = FastAPI(
    title="Example API",
    description="An example API with documentation",
    version="1.0.0"
)

# Configure the documentation
config = DocsConfig(
    docs_dir="./sample_docs",
    title="Example Docs",
    description="Sample documentation for fastapi-docs",
    copyright_text="© 2025 Your Company. All rights reserved.",
    footer_links=[
        ("GitHub", "https://github.com/your-org/your-repo"),
        ("Support", "mailto:support@example.com"),
    ],
    auto_refresh=True,  # Enable hot-reload during development
    enable_search=True,
    syntax_theme="default",  # Try: monokai, friendly, colorful
)

# Mount the documentation router
app.include_router(create_docs_router(config), prefix="/userdocs")


@app.get("/")
async def root():
    """Redirect root to documentation."""
    return RedirectResponse(url="/userdocs")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
