import weaviate
from weaviate.auth import Auth
from weaviate.client_base import ConnectionParams
import weaviate.classes as wvc


weaviate_url = "https://yk800nalqwyizpyqiipfw.c0.europe-west3.gcp.weaviate.cloud"
weaviate_api_key = "r7ulnPvkmroOfUB1LnvcD5xu5HViFUYtrDqM"

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

def ensure_client_connected():
    if not client.is_connected():
        print("Client is not connected. Connecting to Weaviate...")
        client.connect()
        print("Weaviate is connected")


def client_article():
    try:
        paragraphs = client.collections.create(
            name="Data_base_paragraphs",
            vectorizer_config=wvc.config.Configure.Vectorizer.none())
    except Exception as e:
        print(e)



