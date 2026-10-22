# Toolchain image for EXEC_BACKEND=docker. Build, then pin the resulting image
# id in EXEC_CONTAINER_IMAGE:
#   docker build -t dsa-verification:<date> sandbox/
#
# Python, Node, Java, C, C++ and Rust come from Debian. Ruby is Debian's.
# Go and the .NET SDK are copied from the official images, TypeScript from an
# npm install, all pinned by digest so the image builds the same way twice.
FROM node:18-bookworm-slim@sha256:f9ab18e354e6855ae56ef2b290dd225c1e51a564f87584b9bd21dd651838830e AS typescript
RUN npm install -g typescript@5.4.5 --no-audit --no-fund

FROM golang:1.23-bookworm@sha256:167053a2bb901972bf2c1611f8f52c44d5fe7e762e5cab213708d82c421614db AS go

FROM mcr.microsoft.com/dotnet/sdk:8.0@sha256:738f72aff955d5c5690e06b6fc8ecd1b90ead564099a257ac528ff720b8da85f AS dotnet

FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 nodejs openjdk-17-jdk-headless gcc g++ rustc coreutils \
      ruby libicu72 libssl3 zlib1g libstdc++6 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=go /usr/local/go /usr/local/go
COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet
COPY --from=typescript /usr/local/lib/node_modules/typescript /usr/local/lib/typescript
RUN ln -s /usr/local/go/bin/go /usr/local/bin/go \
 && ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet \
 && printf '#!/bin/sh\nexec node /usr/local/lib/typescript/bin/tsc "$@"\n' > /usr/local/bin/tsc \
 && chmod +x /usr/local/bin/tsc
# The sandbox root is read-only, so Go's build cache cannot be created at run
# time and a cold standard-library build would not fit the wall clock. Build the
# commonly imported packages once here; the cache is read-only afterwards.
RUN mkdir -p /opt/gocache /tmp/warm && cd /tmp/warm \
 && printf 'module m\n\ngo 1.21\n' > go.mod \
 && printf 'package main\nimport ("fmt";"strings";"sort";"strconv";"errors";"math";"unicode";"os";"bufio";"sync";"encoding/json";"bytes";"slices";"maps";"container/heap";"container/list";"math/bits";"unicode/utf8";"time";"context";"regexp";"math/rand";randv2 "math/rand/v2";"math/big";"math/cmplx";"log";"flag";"hash/fnv";"hash/crc32";"path";"path/filepath";"encoding/hex";"encoding/binary";"encoding/base64";"container/ring";"crypto/sha256";"crypto/md5";"html";"io";"cmp";"iter";"unicode/utf16";"sync/atomic";"reflect";"runtime";"text/tabwriter";"io/ioutil")\nvar _ = fmt.Sprint\nfunc main(){ _=strings.ToUpper; _=sort.Ints; _=strconv.Itoa; _=errors.New; _=math.Abs; _=unicode.IsLetter; _=os.Args; _=bufio.NewReader; var m sync.Mutex; _=&m; _=json.Marshal; _=bytes.NewBuffer; _=slices.Sort[[]int]; _=maps.Keys[map[int]int]; _=heap.Init; _=list.New; _=bits.Len; _=utf8.RuneLen; _=time.Now; _=context.Background; _=regexp.MustCompile; _=rand.Int; _=randv2.IntN; _=big.NewInt; _=cmplx.Abs; _=log.Println; _=flag.Parse; _=fnv.New32; _=crc32.ChecksumIEEE; _=path.Base; _=filepath.Join; _=hex.EncodeToString; _=binary.BigEndian; _=base64.StdEncoding; _=ring.New; _=sha256.Sum256; _=md5.Sum; _=html.EscapeString; _=io.EOF; _=cmp.Compare[int]; _=iter.Pull[int]; _=utf16.Encode; var ai atomic.Int64; _=&ai; _=reflect.TypeOf; _=runtime.NumCPU; _=tabwriter.NewWriter; _=ioutil.Discard }\n' > main.go \
 && GOCACHE=/opt/gocache go build -o /dev/null . && chmod -R a+rX /opt/gocache && rm -rf /tmp/warm
ENV JAVA_TOOL_OPTIONS="-XX:ActiveProcessorCount=1 -XX:ParallelGCThreads=1 -XX:ConcGCThreads=1" \
    GOCACHE=/opt/gocache GOFLAGS=-buildvcs=false GOTOOLCHAIN=local \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 \
    DOTNET_EnableDiagnostics=0 DOTNET_TieredPGO=0
WORKDIR /work
