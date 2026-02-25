"""Configuration for AI Tracker."""

import os
from pathlib import Path
from typing import Final

# Project paths
PROJECT_ROOT: Final[Path] = Path(__file__).parent
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
DAILY_DIR: Final[Path] = DATA_DIR / "daily"
HISTORY_DIR: Final[Path] = DATA_DIR / "history"
PROJECTS_FILE: Final[Path] = DATA_DIR / "projects.json"

# GitHub API
GITHUB_TOKEN: Final[str] = os.getenv("GITHUB_TOKEN", "")

# Search keywords for AI projects
AI_KEYWORDS: Final[list[str]] = [
    "llm",
    "large language model",
    "gpt",
    "transformer",
    "diffusion",
    "stable diffusion",
    "AI",
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "chatbot",
    "langchain",
    "llama",
    "mistral",
    "claude",
    "gemini",
]

# Trending languages to monitor
TRENDING_LANGUAGES: Final[list[str]] = [
    "Python",
    "TypeScript",
    "JavaScript",
    "Jupyter Notebook",
    "Rust",
    "Go",
]

# Watchlist: Known significant AI projects
WATCHLIST: Final[list[str]] = [
    # LLMs & Chatbots
    "langchain-ai/langchain",
    "langchain-ai/langgraph",
    "huggingface/transformers",
    "vllm-project/vllm",
    "ollama/ollama",
    "meta-llama/llama",
    "mistralai/mistral-src",
    "anthropics/claude-code",
    "google/gemma",
    
    # Diffusion & Image
    " StabilityAI/StableDiffusion",
    " StabilityAI/stable-video-diffusion",
    "comfyanonymous/ComfyUI",
    "AUTOMATIC1111/stable-diffusion-webui",
    
    # Agents & Automation
    "OpenDevin/OpenDevin",
    "ServiceNow/AgentPay",
    "babyagi/babyagi",
    
    # RAG & Knowledge
    "run-llama/llama_index",
    "milvus-io/milvus",
    "chroma-core/chroma",
    
    # Training & Fine-tuning
    "axolotl-ai/axolotl",
    "mlabonne/llm-course",
    
    # AI Infrastructure
    "pytorch/pytorch",
    "tensorflow/tensorflow",
    "keras-team/keras",
    "ray-project/ray",
    "predibase/lorax",
]

# Rate limiting
API_RATE_LIMIT_BUFFER: Final[int] = 100  # Keep this many requests in reserve
CACHE_TTL_SECONDS: Final[int] = 3600  # 1 hour

# Data retention
MAX_DAILY_REPORTS: Final[int] = 90  # Keep 90 days of daily reports
