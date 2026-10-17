FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 nodejs openjdk-17-jdk-headless gcc g++ rustc coreutils \
 && rm -rf /var/lib/apt/lists/*
ENV JAVA_TOOL_OPTIONS="-XX:ActiveProcessorCount=1 -XX:ParallelGCThreads=1 -XX:ConcGCThreads=1"
WORKDIR /work
