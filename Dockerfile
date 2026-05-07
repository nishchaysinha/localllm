FROM nvidia/cuda:12.6.3-devel-ubuntu24.04 AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    git cmake build-essential pkg-config \
    libcurl4-openssl-dev libssl-dev libopenblas-dev curl \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/local/cuda/lib64/stubs/libcuda.so \
           /usr/local/cuda/lib64/stubs/libcuda.so.1 \
    && echo "/usr/local/cuda/lib64/stubs" > /etc/ld.so.conf.d/cuda-stubs.conf \
    && ldconfig

RUN git clone --depth 1 https://github.com/TheTom/llama-cpp-turboquant.git /llama.cpp

WORKDIR /llama.cpp
RUN cmake -B build \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=ON \
        -DGGML_CUDA=ON \
        -DGGML_BLAS=ON \
        -DGGML_CCACHE=OFF \
        -DLLAMA_BUILD_TESTS=OFF \
        -DLLAMA_BUILD_EXAMPLES=OFF \
        -DLLAMA_BUILD_SERVER=ON \
    && cmake --build build --config Release -j$(nproc) --target llama-server

FROM nvidia/cuda:12.6.3-runtime-ubuntu24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4 libgomp1 libssl3t64 libopenblas0 curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /llama.cpp/build/bin/ /app/
COPY --from=build /llama.cpp/build/src/*.so* /app/
COPY --from=build /llama.cpp/build/ggml/src/*.so* /app/
RUN echo "/app" > /etc/ld.so.conf.d/llama.conf && ldconfig

ENTRYPOINT ["/app/llama-server"]
