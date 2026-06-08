#!/bin/bash


API_URL="http://localhost:5000/trader-api/v1"
IMAGE_NAME="deepseek-trader"
CONTAINER_NAME="trading-agent-1"
PORT=5000
APP_USER=user
APP_PASS=changeit

finish() {
  echo ""
  read -n 1 -s -r -p "Press any key to exit..."
}
trap finish EXIT

case "$1" in
  start)
    echo "Launching DeepSeek R1..."

    sleep 2

    # Download model
    MODEL_DIR="models"
    MODEL_FILE="model.gguf"
    MODEL_URL="https://huggingface.co/unsloth/DeepSeek-R1-Distill-Qwen-14B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf"

    if [ ! -d "$MODEL_DIR" ]; then
      echo "Creating $MODEL_DIR directory..."
      mkdir -p "$MODEL_DIR"
    fi

    # Check if the model file exists, download if it doesn't
    if [ ! -f "$MODEL_DIR/$MODEL_FILE" ]; then
      echo "Model not found locally, downloading..."
      
      curl -L -# -o "$MODEL_DIR/$MODEL_FILE" "$MODEL_URL"
      
      if [ $? -ne 0 ]; then
          echo "Error: Failed to download the model via curl."
          rm -f "$MODEL_DIR/$MODEL_FILE" 
          exit 1
      fi
      echo "Download complete!"
      
      # Handle failures
      if [ $? -ne 0 ]; then
          echo "Error: Failed to download the model. Double check the URL or your connection."
          # Clean up the partial/corrupted file if wget failed
          rm -f "$MODEL_DIR/$MODEL_FILE" 
          exit 1
      fi
      echo "Download complete!"
    else
      echo "Model $MODEL_FILE already exists. Skipping download."
    fi

    # Check if the image already exists locally
    if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
      echo "LLM image '$IMAGE_NAME' not found locally. Building from Dockerfile..."
      docker build -t "$IMAGE_NAME" --rm .
      
      if [ $? -ne 0 ]; then
        echo "Error: Docker build failed for image=$IMAGE_NAME."
        exit 1
      fi
      echo "Build complete."
    else
      echo "Docker image '$IMAGE_NAME' already exists. Skipping build."
    fi

    # Launch the python server in the background
    nohup python -u src/deepseek_controller.py > controller.log 2>&1 &
    echo $! > .controller.pid

    sleep 3

    tail -n 20 controller.log

    echo "This usually takes about a minute..."

    # Inject Auth and call /start
    START_STATUS=$(curl -sS -o /dev/null -w "%{http_code}" -u "$APP_USER:$APP_PASS" -X POST "$API_URL/start")
    
    if [ "$START_STATUS" -eq 200 ]; then
      echo -e "LLM server is online! Try it out: './llm-agent.sh chat'"
    else
      echo -e "Failed to start AI. HTTP Status: $START_STATUS."
      docker logs --tail 30 "$CONTAINER_NAME" 2>&1
      echo -e "\nCheck controller.log for more info..."
    fi
    ;;
  
  chat)
    echo "Starting Chat (Type 'exit' to quit)"
    while true; do
      read -p "You: " user_input
      if [ "$user_input" == "exit" ]; then break; fi

      echo -n "Ai is thinking..."

      # invoke LLM
      response=$(curl -sS -u "$APP_USER:$APP_PASS" -X POST "$API_URL/chat" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$user_input\", \"system_prompt\": \"You are an elite quantitative AI.\", \"cache_prompt\": false}")

      echo "$response"
    done
    ;;

  stop)
    echo "Terminating LLM container and Controller..."

    # trigger the Docker shutdown
    response=$(curl -sS -u "$APP_USER:$APP_PASS" -X POST "$API_URL/stop")

    echo $response

    sleep 2

    # Kill the FastAPI server
    if [ -f .controller.pid ]; then
      kill $(cat .controller.pid)
      rm .controller.pid
      echo "All systems offline. VRAM cleared."
    else
      echo "No running controller found"
    fi

    # Workaround: clean up processes on PORT 5000
    GHOST_PID=$(netstat -ano | grep ":$PORT" | grep "LISTENING" | awk '{print $5}' | head -n 1)

    if [ ! -z "$GHOST_PID" ]; then
        echo "Found ghost process $GHOST_PID on PORT $PORT. Evicting..."
        taskkill //F //T //PID $GHOST_PID
        sleep 1
    fi
    ;;
  
  *)
    echo "Usage: ./llm-agent.sh {start|chat|stop}"
    ;;
esac
