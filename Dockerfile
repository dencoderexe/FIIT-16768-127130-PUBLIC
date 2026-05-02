# ===STAGE1===
FROM debian:bookworm-slim AS prebuilder

USER root
WORKDIR /tmp

# install building dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    tar \
    && rm -rf /var/lib/apt/lists/*

# download MSIsensor v0.6
RUN curl -L https://github.com/ding-lab/msisensor/releases/download/0.6/msisensor.linux \
    -o msisensor

# download and compile fixed RepeatFinder source code
RUN curl -L https://github.com/dencoderexe/MANTIS/archive/31e626a.tar.gz \
    -o mantis.tar.gz && \
    tar -xzf mantis.tar.gz && \
    make -C MANTIS-31e626a121d6515345503d0f515aaf6c409dba75/tools

# ===STAGE2===
FROM mambaorg/micromamba:2.5.0

USER root
WORKDIR /app

# set up Python environments and install MSI tools via micromamba
COPY env-base.yaml /tmp/env-base.yaml
COPY env-mantis.yaml /tmp/env-mantis.yaml

RUN micromamba install -y -n base -f /tmp/env-base.yaml && \
    micromamba create -y -n mantis -f /tmp/env-mantis.yaml && \
    micromamba clean --all --yes

# runtime dependency for msisensor
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# copy MSIsensor (update 0.5->0.6)
COPY --from=prebuilder /tmp/msisensor /opt/conda/bin/msisensor

# copy RepeatFinder
COPY --from=prebuilder /tmp/MANTIS-31e626a121d6515345503d0f515aaf6c409dba75/tools/RepeatFinder /opt/conda/bin/RepeatFinder

# make them executable
RUN chmod +x /opt/conda/bin/msisensor /opt/conda/bin/RepeatFinder

COPY . /app

ENV PYTHONUNBUFFERED=1
EXPOSE 8050

CMD ["python", "app.py"]
