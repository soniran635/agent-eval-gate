import requests

def call_local_llm(prompt: str, system_prompt: str = "You are a helpful AI assistant.", model: str = "llama3.2:3b") -> str:
    """Calls local Ollama API running on localhost:11434 with zero external costs."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Error: {str(e)}"
