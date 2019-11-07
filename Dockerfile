FROM python:3.7 as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_CREATE=false
# POETRY_VERSION=0.12.11

ENV PYTHONPATH=/app/src

# system deps
# RUN pip install "poetry"
# RUN pip install "poetry==$POETRY_VERSION"
# RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
# RUN poetry self:update --preview

# Install Poetry & ensure it is in $PATH
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | POETRY_PREVIEW=1 python
ENV PATH "/root/.poetry/bin:/opt/venv/bin:${PATH}"



# copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
# COPY requirements.txt /app/

# project initialization
# RUN poetry config settings.virtualenvs.create false
RUN poetry install --no-dev --no-interaction
# RUN pip install -r requirements.txt


RUN mkdir /app/src && touch /app/src/__init__.py

# make project source symlinks
RUN poetry install --no-dev --no-interaction

# copy project files
COPY . /app

# create unprivileged user
# RUN adduser --disabled-password --gecos '' celeryuser
RUN groupadd -r celeryuser && useradd -r -m -g celeryuser celeryuser
RUN find /app ! -user celeryuser -exec chown celeryuser {} \;