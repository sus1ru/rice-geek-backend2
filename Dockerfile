# Pull base image
FROM python:3.10.2-slim-bullseye
LABEL maintainer="susiru"

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY ./requirements.txt /tmp/requirements.txt

RUN apt-get -y update && \
    apt-get -y install \
        curl \
        libpangocairo-1.0-0 \
        libpq-dev \
        python-dev \
        libproj-dev \
        libc-dev \
        binutils \
        gettext \
        make \
        cmake \
        gcc \
        gdal-bin \
        libgdal-dev \
        g++ && \
    pip install --use-pep517 -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
        mkdir -p /vol/web/media && \
        mkdir -p /vol/web/static && \
        chown -R django-user:django-user /vol && \
        chmod -R 755 /vol


# Set work directory
COPY ./app /app
WORKDIR /app
EXPOSE $PORT

# ENV PATH="/py/bin:$PATH"
USER django-user
