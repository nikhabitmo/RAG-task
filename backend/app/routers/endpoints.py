import json
from typing import List
from weaviate.classes.query import Filter
from fastapi import APIRouter

from ..database.database import ensure_client_connected, client
from ..embending.embending import embed_text, extract_keywords
from ..models.models import Document, SearchQuery

router = APIRouter()


@router.post("/indexing")
async def index_docs_with_embeddings(json_input: List[Document]):
    try:
        ensure_client_connected()
        for item in json_input:
            document = Document(content=item.content, dataframe=item.dataframe,
                                keywords=item.keywords)

            embedding = embed_text(document.content)
            with client.batch.dynamic() as batch:
                batch.add_object(
                    properties={
                        "content": document.content,
                        "dataframe": document.dataframe,
                        "keywords": document.keywords,
                    },
                    vector=embedding.tolist(),
                    collection="Data_base_paragraphs"
                )
        return {"message": "Documents indexed with embeddings"}
    except Exception as e:
        print(f"Failed to add document: {e}")
        if client.batch.failed_objects:
            print("Failed objects:", client.batch.failed_objects)
        return {"error": f"Document failed to index: {e}"}


@router.post("/searching")
async def search_with_llm(query: SearchQuery):
    ensure_client_connected()
    text = query.text
    filter_by = query.filter_by
    top_k = query.top_k
    keywords = query.keywords

    query_embedding = embed_text(text)
    if not keywords:
        keywords = extract_keywords(text)

    paragraphs = client.collections.get("Data_base_paragraphs")
    result = paragraphs.query.hybrid(
        query=text,
        filters=(
            Filter.all_of([
                Filter.by_property("dataframe").contains_any(filter_by),
                # Filter.by_property("keywords").contains_any(keywords)
            ])
        ),
        vector=query_embedding,
        limit=top_k
    )

    seen = set()
    unique_objects = []
    for obj in result.objects:
        obj_properties_json = json.dumps(obj.properties, sort_keys=True)

        if obj_properties_json not in seen:
            seen.add(obj_properties_json)
            unique_objects.append(obj.properties)

    return {"response": unique_objects}
