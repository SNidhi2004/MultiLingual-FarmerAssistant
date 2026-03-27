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
        q_text = qa.get("question_user") or qa.get("question", "")
        a_text = qa.get("answer_user") or qa.get("answer", "")
        
        # Filter out refusals so the LLM doesn't latch onto them
        lower_a = a_text.lower()
        refusal_keywords = [
            "unable to answer", "cannot answer", "can't answer", 
            "consult", "refuse", "unrelated"
        ]
        if any(keyword in lower_a for keyword in refusal_keywords):
            continue
            
        history_block += f"Q: {q_text}\nA: {a_text}\n"
        

    prompt = f"""
You are an agricultural assistant for farmers.

STRICT RULES:
- Answer ONLY about the detected disease.
- If the question is unrelated, politely refuse by saying "I cannot answer this question".
- Be concise and practical.
- Do NOT invent new diseases or facts.
- Remove the '*' symbols when giving the answer.
- Every time make it farmer friendly and use simple language. Try to avoid technical terms.
- Base your answer ONLY on the current question. Ignore any past refusals.

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

    try:
        prompt = build_prompt(
            disease=disease,
            confidence=confidence,
            last_qa=last_qa,
            question=question
        )
        
        print(f"Prompt built, sending to Ollama...")
        response = query_gemma(prompt)
        
        # Final guardrail
        if not response:
            return (
                "I'm unable to answer that right now. "
                "Please consult an agriculture officer."
            )
        
        return response.strip()
        
    except Exception as e:
        print(f"Error in generate_answer: {e}")
        return "I'm having trouble answering right now. Please try again."
