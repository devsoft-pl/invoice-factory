FROM python:3.11-slim-bullseye as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PIP_DEFAULT_TIMEOUT 100
ENV POETRY_VIRTUALENVS_IN_PROJECT 1
ENV POETRY_NO_INTERACTION 1
ENV POETRY_HOME="/opt/poetry"
ENV VENV_PATH="/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update &&\
    apt-get install --no-install-recommends -y curl &&\
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc &&\
    echo "deb https://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main" \
      > /etc/apt/sources.list.d/postgresql.list &&\
    apt-get install --no-install-recommends -y postgresql-client redis-tools netcat-openbsd vim gettext &&\
    groupadd -f -g 11111 app &&\
    useradd -l -u 11111 -g app -d /app -m app &&\
    chown -R app:app /app &&\
    curl -sSL https://install.python-poetry.org | python -

FROM base as builder-deps

RUN apt-get install build-essential --no-install-recommends -y

COPY poetry.lock pyproject.toml ./
RUN poetry install --only main && poetry add psycopg2-binary

FROM base AS runtime
COPY --from=builder-deps $VENV_PATH $VENV_PATH

USER app
WORKDIR /app
EXPOSE 8000

COPY --chown=app:app . .
RUN python manage.py compilemessages

ENTRYPOINT ["/app/deployment/entrypoint.sh"]