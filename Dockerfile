FROM python:3.9-slim-buster
EXPOSE 80

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app
ENV VIRTUAL_ENV /app/.venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

COPY requirements.txt .

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

WORKDIR ${APP_HOME}

COPY src src
COPY main.py .
COPY docker-entrypoint.sh .
COPY api.json /tmp/api_key.json


ENTRYPOINT ["/bin/bash"]
CMD ["./docker-entrypoint.sh"]