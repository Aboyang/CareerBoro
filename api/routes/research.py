from fastapi import APIRouter
from services.research import Research
from schemas.research import (
    SearchRequest,
    ReadRequest,
    SummariseRequest,
    FullResearchRequest
)

router = APIRouter(prefix="/research", tags=["Research"])

researcher = Research()

# Search URLs
@router.post("/search")
def search_webpages(req: SearchRequest):
    urls = researcher.find_webpages(req.query, req.limit)
    return {"urls": urls}


# Extract webpage content
@router.post("/read")
def read_webpage(req: ReadRequest):
    content = researcher.read_html(req.url, req.char_limit)
    return {"content": content}


# Summarise content
@router.post("/summarise")
def summarise(req: SummariseRequest):
    summary = researcher.summarise_page(req.content)
    return {"summary": summary}


# FULL PIPELINE (most useful)
@router.post("/")
def full_research(req: FullResearchRequest):
    urls = researcher.find_webpages(req.query, req.limit)

    results = []

    for url in urls:
        content = researcher.read_html(url, req.char_limit)
        summary = researcher.summarise_page(content)

        results.append({
            "url": url,
            "summary": summary
        })

    return {
        "query": req.query,
        "results": results
    }