from services.ollama_llm import query_gemma


def build_prompt(
    disease: str,
    confidence: float,
    last_qa: list,
    question: str
) -> str:
    """
    Builds a controlled prompt for Gemma:2B.
    All reasoning happens in English.
    """

    history_block = ""
    for qa in last_qa:
        history_block += (
            f"Q: {qa['question']}\n"
            f"A: {qa['answer']}\n"
        )

    prompt = f"""
You are an agricultural assistant for farmers.

STRICT RULES:
- Answer ONLY about the detected disease.
- If the question is unrelated, politely refuse.
- Be concise and practical.
- Do NOT invent new diseases or facts.
- Remove the '*' symbols when giving the answer.
- Evertime make it farmer friendly and use simple language. Try not avoid technical terms.

CONTEXT:
Detected Disease: {disease}
Confidence: {int(confidence * 100)}%

RECENT CONTEXT (last questions):
{history_block if history_block else "None"}

FARMER QUESTION:
{question}

ANSWER:
"""

    return prompt.strip()


def generate_answer(
    disease: str,
    confidence: float,
    last_qa: list,
    question: str
) -> str:
    """
    Generates a safe answer using Gemma:2B.
    """

    prompt = build_prompt(
        disease=disease,
        confidence=confidence,
        last_qa=last_qa,
        question=question
    )

    response = query_gemma(prompt)

    # Final guardrail (simple but effective)
    if not response:
        return (
            "I’m unable to answer that right now. "
            "Please consult an agriculture officer."
        )

    return response.strip()
