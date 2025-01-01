FROM python:3.10

ARG MEDIA_PATH
ARG GID=101
ENV USER=sd_solutions_user
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get -y update && adduser --gid ${GID} --shell /bin/bash --disabled-password ${USER}

COPY --chown=${USER}:${GID} gunicorn.conf.py /gunicorn/gunicorn.conf.py

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=${USER}:${GID} ./src /src

WORKDIR /src

USER ${USER}:${GID}

EXPOSE 8000
CMD ["sh", "-c", "gunicorn main:app --config /gunicorn/gunicorn.conf.py"]