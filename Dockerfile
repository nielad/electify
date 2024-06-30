# Stage 1: Base image with dependencies installed

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

# Stage 2: Production image
FROM base as production

#CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
CMD ["sh", "-c", "service cron start && /src/add_cron_job.sh && python get_current_polls.py && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
