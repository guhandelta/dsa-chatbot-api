# Digest-pinned, multi-language toolchain for EXEC_BACKEND=docker.
# Build a local image, then set EXEC_CONTAINER_IMAGE to its image ID digest.
#   docker build -t dsa-verification:<date> sandbox/
#   docker image inspect dsa-verification:<date> --format '{{.Id}}'

FROM node:18-bookworm-slim@sha256:f9ab18e354e6855ae56ef2b290dd225c1e51a564f87584b9bd21dd651838830e AS typescript
RUN npm install -g typescript@5.4.5 --no-audit --no-fund

FROM golang:1.23-bookworm@sha256:167053a2bb901972bf2c1611f8f52c44d5fe7e762e5cab213708d82c421614db AS go

FROM mcr.microsoft.com/dotnet/sdk:8.0@sha256:738f72aff955d5c5690e06b6fc8ecd1b90ead564099a257ac528ff720b8da85f AS dotnet

# The old Debian Java and Rust packages exposed binaries but failed real
# compiler probes in the ARM64 sandbox. Use the upstream, architecture-aware
# toolchain images instead.
FROM eclipse-temurin@sha256:91011320978c10ec51d2cde1eb6f616db6d2a739a0e521096c343dd3fed9abe6 AS java
FROM rust@sha256:86234e857a413004348b471d11a4ebe1aa92d2eae2b6b143cac68fd1ac3c48be AS rust
FROM dart@sha256:0dacdef11e382f5e3842c2e6198daf5f234e55b1e38ccff1143008823949bcc9 AS dart
FROM swift@sha256:196b29e985d0fbdeb427d4898f08ed73b0079c9ac7c37ebdd3bc05fe4e9d784b AS swift

# Kotlin and Scala distributions are version-pinned and checksum-verified.
FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587 AS jvm_extras
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl unzip \
 && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL --retry 3 -o /tmp/kotlin.zip https://github.com/JetBrains/kotlin/releases/download/v2.4.21/kotlin-compiler-2.4.21.zip \
 && echo '7cc140e76daf416a0424a5557f99afd7ca89ebd463ea1101261e3e01c33e75cd  /tmp/kotlin.zip' | sha256sum -c - \
 && unzip -q /tmp/kotlin.zip -d /opt \
 && rm /tmp/kotlin.zip
RUN curl -fsSL --retry 3 -o /tmp/scala.tgz https://github.com/scala/scala/releases/download/v2.13.18/scala-2.13.18.tgz \
 && echo '1834d09fd5c78ec77e9a933ab76c724280a8ec9595a332a6112823787a9ac3e6  /tmp/scala.tgz' | sha256sum -c - \
 && tar -xzf /tmp/scala.tgz -C /opt \
 && rm /tmp/scala.tgz

# Swift's full official image supplies the compiler and libraries it needs.
# The slim variant contains only runtime components. GHC comes from Debian.
FROM swift@sha256:196b29e985d0fbdeb427d4898f08ed73b0079c9ac7c37ebdd3bc05fe4e9d784b
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 nodejs gcc g++ coreutils php-cli ruby ghc libstdc++6 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=java /opt/java/openjdk /opt/java/openjdk
COPY --from=rust /usr/local/cargo /usr/local/cargo
COPY --from=rust /usr/local/rustup /usr/local/rustup
COPY --from=dart /usr/lib/dart /usr/lib/dart
COPY --from=typescript /usr/local/lib/node_modules/typescript /usr/local/lib/typescript
COPY --from=go /usr/local/go /usr/local/go
COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet
COPY --from=jvm_extras /opt/kotlinc /opt/kotlinc
COPY --from=jvm_extras /opt/scala-2.13.18 /opt/scala-2.13.18

ENV JAVA_HOME=/opt/java/openjdk \
    JAVA_TOOL_OPTIONS="-XX:ActiveProcessorCount=1 -XX:ParallelGCThreads=1 -XX:ConcGCThreads=1" \
    RUSTUP_HOME=/usr/local/rustup CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/swift/usr/bin:/usr/local/cargo/bin:/opt/scala-2.13.18/bin:/opt/kotlinc/bin:/usr/lib/dart/bin:/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin \
    GOCACHE=/opt/gocache GOFLAGS=-buildvcs=false GOTOOLCHAIN=local \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 \
    DOTNET_EnableDiagnostics=0 DOTNET_TieredPGO=0 DART_SUPPRESS_ANALYTICS=true

RUN ln -s /opt/java/openjdk/bin/java /usr/local/bin/java \
 && ln -s /opt/java/openjdk/bin/javac /usr/local/bin/javac \
 && ln -s /usr/local/go/bin/go /usr/local/bin/go \
 && ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet \
 && ln -s /usr/lib/dart/bin/dart /usr/local/bin/dart \
 && ln -s /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc \
 && ln -s /opt/scala-2.13.18/bin/scala /usr/local/bin/scala \
 && ln -s /opt/scala-2.13.18/bin/scalac /usr/local/bin/scalac \
 && printf '#!/bin/sh\nexec node /usr/local/lib/typescript/bin/tsc "$@"\n' > /usr/local/bin/tsc \
 && chmod +x /usr/local/bin/tsc \
 && php -r 'function dsa_smoke($a, $b) { return $a * $b; } if (dsa_smoke(3, 4) !== 12) { exit(1); }' \
 && for tool in python3 node java javac gcc g++ rustc ruby go dotnet tsc php dart ghc kotlinc swiftc scalac scala; do command -v "$tool" >/dev/null || exit 1; done \
 && java -version \
 && javac -version \
 && rustc --version \
 && dart --disable-analytics --version \
 && ghc --version \
 && kotlinc -version \
 && swiftc --version \
 && scalac -version \
 && scala -version

# The sandbox root is read-only, so Go's build cache cannot be created at run
# time and a cold standard-library build would not fit the wall clock. Build the
# commonly imported packages once here; the cache is read-only afterwards.
RUN mkdir -p /opt/gocache /tmp/warm && cd /tmp/warm \
 && printf 'module m\n\ngo 1.21\n' > go.mod \
 && printf 'package main\nimport ("fmt";"strings";"sort";"strconv";"errors";"math";"unicode";"os";"bufio";"sync";"encoding/json";"bytes";"slices";"maps";"container/heap";"container/list";"math/bits";"unicode/utf8";"time";"context";"regexp";"math/rand";randv2 "math/rand/v2";"math/big";"math/cmplx";"log";"flag";"hash/fnv";"hash/crc32";"path";"path/filepath";"encoding/hex";"encoding/binary";"encoding/base64";"container/ring";"crypto/sha256";"crypto/md5";"html";"io";"cmp";"iter";"unicode/utf16";"sync/atomic";"reflect";"runtime";"text/tabwriter";"io/ioutil")\nvar _ = fmt.Sprint\nfunc main(){ _=strings.ToUpper; _=sort.Ints; _=strconv.Itoa; _=errors.New; _=math.Abs; _=unicode.IsLetter; _=os.Args; _=bufio.NewReader; var m sync.Mutex; _=&m; _=json.Marshal; _=bytes.NewBuffer; _=slices.Sort[[]int]; _=maps.Keys[map[int]int]; _=heap.Init; _=list.New; _=bits.Len; _=utf8.RuneLen; _=time.Now; _=context.Background; _=regexp.MustCompile; _=rand.Int; _=randv2.IntN; _=big.NewInt; _=cmplx.Abs; _=log.Println; _=flag.Parse; _=fnv.New32; _=crc32.ChecksumIEEE; _=path.Base; _=filepath.Join; _=hex.EncodeToString; _=binary.BigEndian; _=base64.StdEncoding; _=ring.New; _=sha256.Sum256; _=md5.Sum; _=html.EscapeString; _=io.EOF; _=cmp.Compare[int]; _=iter.Pull[int]; _=utf16.Encode; var ai atomic.Int64; _=&ai; _=reflect.TypeOf; _=runtime.NumCPU; _=tabwriter.NewWriter; _=ioutil.Discard }\n' > main.go \
 && GOCACHE=/opt/gocache go build -o /dev/null . \
 && chmod -R a+rX /opt/gocache \
 && rm -rf /tmp/warm

WORKDIR /work
