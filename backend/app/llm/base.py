"""LLM abstraction layer.

Defines the only interface anything in the agent (currently the Planner's
SlotExtractor; potentially other LLM-backed components later) is allowed
to depend on. No provider SDK (openai, anthropic, google-generativeai,
ollama's client, ...) should be imported outside app/llm/providers/ —
swapping providers means adding/choosing a provider module via
app/llm/factory.py, never touching a caller.
"""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        """Return the model's raw text completion for the given prompts.

        Deliberately minimal: callers only ever see plain text back.
        Structured-output parsing (e.g. treating the response as JSON) is
        the caller's responsibility, not this interface's — that keeps
        LLMClient reusable for prompts that aren't extraction.
        """
