FROM python:3.11

RUN DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y tzdata \
    && apt-get clean

RUN mkdir /root/.pip
RUN mkdir /app
COPY ./main.py ./requirements.txt ./alembic.ini /app/
COPY ./awx_demo /app/awx_demo/
COPY ./images /app/images/
COPY ./migrations /app/migrations/
COPY ./pip.conf /root/.pip/pip.conf
RUN pip install -U pip \
    && pip install -r /app/requirements.txt

WORKDIR /app

CMD python3 /app/main.py
