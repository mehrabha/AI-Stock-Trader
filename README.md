# AI Portfolio Manager for Risk-Adjusted Trading

## Overview
This project implements an autonomous trading agent that leverages a locally hosted Large Language Model (LLM). The system is split into two components:

1. A deterministic python trading agent.
2. A local LLM server running a quantized 14B parameter model which serves as the reasoning engine.

Script is setup to download **DeepSeek-R1-Distill-Qwen-14b-q4** model from huggingface.co, which requires 12GB of VRAM. You can specify an alternate download link directly in ```llm-agent.sh```.

## Requirements
- Python 3.14+
- Polygon.io/Massive API account
- NVIDIA Graphics Gard with at least 12GB of memory
- Docker Desktop

## Getting Started
### 1. Setup a python virtual environment and install required dependencies:
```
python -m venv venv

# Mac/Linux:
source venv/bin/activate  
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Start the LLM server:
Ensure **Docker Desktop** is running on your machine before proceeding!
```
./llm-agent.sh start

# to verify it is up and accepting requests
./llm-agent.sh chat
```
**Note:** It may take up to 2 minutes  to fully initialize._


### 3. App Configs
Update the .env file in the project root directory and provide your API key:
```
POLYGON_API_KEY=replace_key
```
Application will run into 401 errors in case of invalid keys!

### 4. Run the Autonomous Trading Agent
```
main.py
```
Agent will run a series of validations against the historical market before transitioning into real-time paper trading. You should start seeing logs of the agent actively fetching live market data, and invoking the LLM for trading decisions!