from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    limit: int = 2


class ReadRequest(BaseModel):
    url: str
    char_limit: int = 500


class SummariseRequest(BaseModel):
    content: str


class FullResearchRequest(BaseModel):
    query: str
    limit: int = 3
    char_limit: int = 500