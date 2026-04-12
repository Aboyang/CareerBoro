from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class ReadRequest(BaseModel):
    url: str
    char_limit: int = 2000


class SummariseRequest(BaseModel):
    content: str


class FullResearchRequest(BaseModel):
    query: str
    limit: int = 3
    char_limit: int = 3000