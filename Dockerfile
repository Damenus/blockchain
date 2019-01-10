# Building rpc-perf.
FROM centos:7 AS rpc-perf

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH \
    RUST_VERSION=1.26.2

RUN yum install -y gcc git make wget patch

RUN curl https://sh.rustup.rs -sSf | \
    sh -s -- --default-toolchain stable -y

RUN git clone https://github.com/twitter/rpc-perf.git
WORKDIR /rpc-perf
RUN git checkout 1f77023337ab3c6904c3730546bdd2f31aca9f2d
ADD /workloads/rpc_perf/intel_rpc-perf.patch .
RUN git apply intel_rpc-perf.patch

RUN git clone https://github.com/brayniac/tic
WORKDIR /rpc-perf/tic
RUN git checkout 6a3cf06673e87ec466b59b21655dff6e03a31743
ADD /workloads/rpc_perf/intel_rpc-perf-tic.patch .
RUN git apply intel_rpc-perf-tic.patch
WORKDIR /rpc-perf

RUN git clone https://github.com/brayniac/ratelimit.git
WORKDIR /rpc-perf/ratelimit
RUN git checkout 0bf70c3ab557bf601a7eea836892a5f4828a10ef
ADD /workloads/rpc_perf/intel_rpc-perf-ratelimit.patch .
RUN git apply intel_rpc-perf-ratelimit.patch
WORKDIR /rpc-perf

RUN cargo build --release

# Builing final container that consists of workloads only.
FROM centos:7

RUN yum install -y epel-release
RUN yum makecache
RUN yum install -y python36

ADD /dist/rpc_perf_wrapper.pex /usr/bin/
ADD /workloads/rpc_perf/rpc-perf.toml /etc/
COPY --from=rpc-perf /rpc-perf/target/release/rpc-perf /usr/bin/
COPY --from=rpc-perf /rpc-perf/configs /etc/rpc-perf/