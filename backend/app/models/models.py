from typing import List, Optional
from pydantic import BaseModel


class SearchQuery(BaseModel):
    text: str
    keywords: List[str]
    filter_by: Optional[List[str]] = []
    top_k: int


class Document(BaseModel):
    content: str
    dataframe: str = None
    keywords: list[str] = []


class IndexRequest(BaseModel):
    dataset_name_or_docs: List[Document]
