FROM python:3.12-alpine3.19
LABEL maintainer="majidnoorani"

ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8015

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --default-timeout=100 --upgrade pip && \
    # deps for psycopg2
    apk add --update --no-cache postgresql-client jpeg-dev && \
    # linux-headers is added for WSGI
    apk add --update --no-cache --virtual .tmp-build-deps\
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers&& \
    /py/bin/pip install --default-timeout=100 --retries=3 -r /tmp/requirements.txt && \
    # /py/bin/pip install /downloads/django-richtextfield-1.6.2.tar.gz && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install --default-timeout=100 --retries=3 -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

# CMD ["run.sh"]
