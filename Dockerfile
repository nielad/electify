ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY /src/ /src/

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
