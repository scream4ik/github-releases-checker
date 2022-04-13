FROM python:3.9.12-slim AS compile-image
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt update \
    \
    && apt install -y
COPY ./requirements.txt requirements.txt
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9.12-slim AS build-image
RUN apt update \
    \
    && apt install -y
RUN groupadd -r -g 1001 app && useradd -r -u 1001 -g app app
USER app
COPY --chown=app:app --from=compile-image /opt/venv /opt/venv
COPY --chown=app:app . /app
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"
