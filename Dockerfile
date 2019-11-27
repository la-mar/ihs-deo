FROM python:3.7 as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.0.0b7

ENV PYTHONPATH "/app:/app/src"

# install netcat
RUN apt-get update && \
    apt-get -y install netcat && \
    apt-get clean

RUN pip install "poetry==$POETRY_VERSION"

ENV PATH "/root/.poetry/bin:/opt/venv/bin:${PATH}"

# copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry install --no-dev --no-interaction
RUN mkdir /app/src && touch /app/src/__init__.py

# make project source symlinks
RUN poetry install --no-dev --no-interaction

# copy project files
COPY . /app

# create unprivileged user
RUN groupadd -r celeryuser && useradd -r -m -g celeryuser celeryuser
RUN find /app ! -user celeryuser -exec chown celeryuser {} \;