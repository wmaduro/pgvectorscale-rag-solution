# Add the prompts
from pydantic import BaseModel, Field
from services.llm_factory import LLMFactory

"""
Function to generate a document summary using LLM
https://www.anthropic.com/news/contextual-retrieval
"""

SUMMARY_PROMPT = """
<document>
{doc_content}
</document>

Please provide a concise summary of the above document in 2-3 sentences.
Answer with just the summary, nothing else.
"""

llm = LLMFactory("openai")


class DocumentSummary(BaseModel):
    """Model for document summary response."""

    summary: str = Field(description="Summary of the article")


def generate_summary(article: str) -> str:
    """
    Generate a concise summary of an article using OpenAI.

    Args:
        article: The full text content of the article to summarize

    Returns:
        str: A concise summary of the article

    Raises:
        ValueError: If article is empty or None
    """
    if not article:
        raise ValueError("Article content cannot be empty")

    messages = [
        {
            "role": "user",
            "content": SUMMARY_PROMPT.format(doc_content=article),
        }
    ]

    return llm.create_completion(
        response_model=str,
        messages=messages,
        max_tokens=256,
    )
