import json

import streamlit as st
import re
from keybert import KeyBERT
import warnings
import requests

warnings.filterwarnings("ignore", category=UserWarning)

kw_model = KeyBERT(model='distilbert-base-nli-mean-tokens')


def extract_keywords(text, top_n=10):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=top_n)
    return [kw[0] for kw in keywords]


page = st.sidebar.selectbox(
    "Выберите страницу",
    ["Индексация документов", "Поиск информации"]
)


def send_data_to_server(paragraphs):
    url = "http://backend:8000/indexing"
    payload = paragraphs
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Ошибка сервера: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": f"Ошибка при отправке данных: {str(e)}"}


def send_search_request(query_text, keywords, tags, top_k):
    url = "http://backend:8000/searching"
    payload = {
        "text": query_text,
        "keywords": keywords,
        "filter_by": tags if tags else [],
        "top_k": top_k
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Ошибка сервера: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": f"Ошибка при отправке запроса: {str(e)}"}


def split_into_paragraphs(text):
    paragraphs = re.split(r'\n\s*\n+|\r\n\s*\r\n+', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    return paragraphs


# --------------------------------
# Страница 1: Индексация документов
# --------------------------------
if page == "Индексация документов":
    st.title("Индексация документов")

    uploaded_file = st.file_uploader("Загрузите документ (.txt)", type="txt")

    tag_option = st.selectbox(
        "Выберите тег",
        options=["Техническая литература",
                 "Энциклопедии и справочники",
                 "Философская и научно-популярная литература",
                 "Фэнтези",
                 "Научная фантастика",
                 "Детективы и триллеры",
                 "Художественная литература",
                 "Романтика",
                 "Приключения", ],
        help="Вы можете выбрать тег, описывающий жанр вашего текста, для дальнейшего использования при поиске"
    )

    if st.button("Загрузить документ"):
        if uploaded_file and tag_option:
            document_text = uploaded_file.read().decode("utf-8")

            paragraphs = split_into_paragraphs(document_text)

            data_to_send = []
            st.write("Обработка файла, пожалуйста, подождите")
            progress_bar = st.progress(0)
            total_paragraphs = len(paragraphs)

            for idx, paragraph in enumerate(paragraphs):
                keywords = extract_keywords(paragraph, top_n=10)
                data_to_send.append({
                    "content": paragraph,
                    "dataframe": tag_option,
                    "keywords": keywords
                })

                progress_bar.progress((idx + 1) / total_paragraphs)

            st.write("Отправка данных на сервер...")
            result = send_data_to_server(data_to_send)

            if "error" in result:
                st.error(f"Ошибка: {result['error']}")
            else:
                st.success(result.get("message", "Данные успешно отправлены!"))
                st.json(result.get("processed_data", []))

            progress_bar.empty()

        else:
            st.error("Пожалуйста, загрузите файл и укажите тег.")



# -------------------------------
# Страница 2: Поиск информации
# -------------------------------
elif page == "Поиск информации":
    st.title("Поиск информации")

    query_text = st.text_area("Введите текст запроса", help="Введите текст для поиска информации.")

    st.subheader("Фильтрация по тегам")
    available_tags = ["Техническая литература",
                      "Энциклопедии и справочники",
                      "Философская и научно-популярная литература",
                      "Фэнтези",
                      "Научная фантастика",
                      "Детективы и триллеры",
                      "Художественная литература",
                      "Романтика",
                      "Приключения", ]
    selected_tags = st.multiselect(
        "Выберите один или несколько тегов из списка (опционально):",
        options=available_tags,
        help="Выберите теги для фильтрации результатов."
    )

    top_k = st.number_input(
        "Количество результатов (Top-K):",
        min_value=1,
        max_value=100,
        value=3,
        step=1,
        help="Укажите количество результатов, которые нужно вернуть."
    )

    if st.button("Найти"):
        if query_text:
            st.write("Извлечение ключевых слов...")
            keywords = extract_keywords(query_text, top_n=10)
            st.write(f"**Ключевые слова:** {', '.join(keywords)}")

            st.write("Отправка запроса на сервер...")
            result = send_search_request(query_text, keywords, selected_tags, top_k)

            if "error" in result:
                st.error(f"Ошибка: {result['error']}")
            else:
                st.success("Поиск выполнен успешно!")
                st.subheader("Результаты:")
                for idx, item in enumerate(result.get("response", []), start=1):
                    st.write(f"**Результат {idx}:**")
                    st.write(f"{item['content']}")
        else:
            st.error("Поле запроса обязательно для выполнения поиска.")
