FROM continuumio/miniconda3:latest AS builder

COPY deploy/conda/environment.yml environment.yml

RUN conda env create -f environment.yml -n dockerflask

FROM debian:latest

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update --yes && \
    apt-get clean

COPY --from=builder /opt/conda/envs/dockerflask /opt/conda/envs/dockerflask

ENV PATH="/opt/conda/envs/dockerflask/bin:$PATH"

WORKDIR /app
COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
