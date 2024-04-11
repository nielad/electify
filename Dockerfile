ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY /src/ /src/

RUN pip install -r requirements.txt
RUN apt-get update \
	&& apt-get install -y cron\
	&& rm -rf /var/lib/apt/lists/*
	
RUN chmod +x add_cron_job.sh
RUN service cron start && add_cron_job.sh

 

# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
CMD ["sh", "-c", "service cron start && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
