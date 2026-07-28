"""OpenAI-backed LLMClient.

The only file allowed to import the `openai` package — everything else in
the codebase depends on the LLMClient interface, not this SDK. The import
is deferred into __init__ so installing `openai` is only required when
this provider is actually selected (LLM_PROVIDER=openai).

`base_url` is accepted so this same client can talk to any
OpenAI-compatible endpoint (e.g. a local Ollama server), not just OpenAI
itself — a straightforward path to "swap the provider" without a new
class for every OpenAI-API-compatible option.
"""

from app.llm.base import LLMClient


class OpenAILLMClient(LLMClient):
    def __init__(self, *, api_key: str, model: str, base_url: str | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The 'openai' package is required for LLM_PROVIDER=openai. "
                "Install it with `pip install openai`."
            ) from exc

        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
