import logging
import subprocess
import time
from contextlib import contextmanager

import ollama
import requests

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "qwen3.8"
OLLAMA_BASE_URL = "http://localhost:11434"


def _is_ollama_running() -> bool:
    try:
        response = requests.get(OLLAMA_BASE_URL, timeout=2)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def start_ollama() -> subprocess.Popen | None:
    if _is_ollama_running():
        logger.info("ollama server already running, skipping start")
        return None

    logger.info("Starting ollama server...")
    proc = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(30):
        if _is_ollama_running():
            logger.info("ollama server ready")
            return proc
        time.sleep(1)

    proc.terminate()
    raise RuntimeError("ollama server did not become ready in time")


def stop_ollama(proc: subprocess.Popen | None, model: str) -> None:
    logger.info(f"Unloading model {model} from GPU...")
    try:
        ollama.chat(model=model, messages=[], keep_alive=0)
    except Exception as e:
        logger.warning(f"Failed to unload model: {e}")

    if proc is not None:
        logger.info("Stopping ollama server...")
        proc.terminate()
        proc.wait()
        logger.info("ollama server stopped")


@contextmanager
def ollama_session(model: str = DEFAULT_MODEL):
    proc = start_ollama()
    try:
        yield
    finally:
        stop_ollama(proc, model)


def generate_prompts_for_theme(
    theme: str,
    count: int,
    color_range: str,
    system_prompt: str,
    task_template: str,
    model: str = DEFAULT_MODEL,
) -> list[str]:
    """Generate `count` image generation prompts for a single theme/style string."""

    user_message = task_template.format(n=count, theme=theme, color_range=color_range)

    logger.debug(f"Querying {model} for theme: {theme!r} color_range: {color_range!r}")

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        think=True,
    )

    thinking = response.message.thinking
    if thinking:
        logger.info(f"<think> {thinking} </think>")

    raw = response.message.content
    prompts = [line.strip() for line in raw.splitlines() if line.strip()]

    logger.info(f"Got {len(prompts)} prompts for theme: {theme!r}")

    return prompts


def generate_prompts_for_themes(
    themes: list[str],
    count: int,
    color_range: str,
    system_prompt: str,
    task_template: str,
    model: str = DEFAULT_MODEL,
) -> list[str]:
    """Generate `count` prompts for each theme, returning a flat list."""

    all_prompts = []

    for theme in themes:
        prompts = generate_prompts_for_theme(
            theme,
            count,
            color_range=color_range,
            system_prompt=system_prompt,
            task_template=task_template,
            model=model,
        )
        all_prompts.extend(prompts)

    return all_prompts
