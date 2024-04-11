ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY /src/ /src/

RUN pip install -r requirements.txt
RUN apt-get update \
	&& apt-get install -y cron\
	&& rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/crontabs \
    && chmod +x /src/get_current_polls.py \
    && echo '* * * * * /usr/bin/python3 /src/get_current_polls.py' >> /etc/crontabs/root \
	&& RUN service cron start

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
