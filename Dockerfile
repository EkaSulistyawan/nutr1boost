# FROM ubuntu:24.04
FROM python:3.11-slim

# Set environment variables
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1


RUN apt-get update \
&& apt-get install -y build-essential libssl-dev libffi-dev python3-dev python3-pip python3-venv

WORKDIR /app
COPY . .

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip3 install \
    langchain \
    langgraph \ 
    langchain-community \
    langchain-google-genai \
    langchain-experimental \
    pandas \
    numpy \
    faiss-cpu \
    tavily-python \
    typing-extensions \
    django-bootstrap-v5 \
    django-cors-headers \
    google-generativeai \
    openai \
    tiktoken \
    nest-asyncio \
    sentence-transformers \
    tabulate


CMD ["python","manage.py","runserver","0.0.0.0:8000"]
