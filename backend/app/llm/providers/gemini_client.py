"""Google Gemini-backed LLMClient.

The only file allowed to import the `google.genai` package — everything
else in the codebase depends on the LLMClient interface, not this SDK.
The import is deferred into __init__ so installing `google-genai` is only
required when this provider is actually selected (LLM_PROVIDER=gemini).
"""

from app.llm.base import LLMClient


class GeminiLLMClient(LLMClient):
    def __init__(self, *, api_key: str, model: str) -> None:
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "The 'google-genai' package is required for LLM_PROVIDER=gemini. "
                "Install it with `pip install google-genai`."
            ) from exc

        self._types = genai.types
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        # response_mime_type is a Gemini-specific optimization requesting
        # syntactically valid JSON output; stays entirely inside this
        # provider, the same role response_format plays in OpenAILLMClient.
        response = self._client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=self._types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
                response_mime_type="application/json",
            ),
        )
        return response.text or ""
