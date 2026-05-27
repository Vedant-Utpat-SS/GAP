import argparse
import os
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from RAG.get_embedding_function import get_embedding_function
import requests

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
You are a contract analysis assistant. The context below contains excerpts from one or more contract documents.
Synthesize information across ALL provided excerpts to answer the question comprehensively.
If the excerpts are from different documents, mention the relevant document names in your answer.

Context:
{context}

---

Question: {question}
"""

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY not set. Get a free key at https://aistudio.google.com/apikey"
        )
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=api_key,
        temperature=0.2,
    )
    response_text = model.invoke(prompt).content

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text

def _send_claude_request(prompt: str, api_key: str | None = None, model: str = "claude-sonnet-4-6", max_tokens: int = 4096, temperature: float = 0.2) -> str:
    """Send a request to Anthropic's Messages API and return the completion text.

    Environment: set `ANTHROPIC_API_KEY` or pass `api_key`.
    """
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    return data["content"][0]["text"].strip()


def query_rag_claude(query_text: str, api_key: str | None = None) -> str:
    """RAG query that uses Anthropic Claude Sonnet (cloud API) instead of the local Ollama model.

    Returns the model output (string).
    """
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.max_marginal_relevance_search(query_text, k=10, fetch_k=40)
    context_parts = []
    for doc in results:
        src = doc.metadata.get("source", doc.metadata.get("id", "unknown"))
        context_parts.append(f"[Source: {os.path.basename(src)}]\n{doc.page_content}")
    context_text = "\n\n---\n\n".join(context_parts)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Call Anthropic
    response_text = _send_claude_request(prompt, api_key=api_key)

    sources = [doc.metadata.get("id", doc.metadata.get("source", None)) for doc in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text

if __name__ == "__main__":
    main()