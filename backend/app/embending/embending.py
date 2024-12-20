from keybert import KeyBERT
from transformers import AutoTokenizer, AutoModel
import torch


# Модель для генерации эмбеддингов
model_name = "intfloat/e5-large-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)


def embed_text(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.squeeze().numpy()


def extract_keywords(text, top_n=10):
    kw_model = KeyBERT(model='distilbert-base-nli-mean-tokens')
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=top_n)
    return [kw[0] for kw in keywords]
