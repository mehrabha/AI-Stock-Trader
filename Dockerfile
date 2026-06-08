# Use the official CUDA server image
FROM ghcr.io/ggml-org/llama.cpp:server-cuda

WORKDIR /app

# Set environment variables for GPU optimization
# These can be overridden at runtime if needed
ENV LLAMA_ARG_N_GPU_LAYERS=99
ENV LLAMA_ARG_CTX_SIZE=16384
ENV LLAMA_ARG_PORT=8080
ENV LLAMA_ARG_HOST=0.0.0.0

EXPOSE 8080

# Mount image folder to access LLM images
ENTRYPOINT ["./llama-server", "-m", "/models/model.gguf"]