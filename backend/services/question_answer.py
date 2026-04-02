from services.ollama_llm import query_gemma


def build_prompt(
    disease: str,
    confidence: float,
    last_qa: list,
    question: str,
    location: str = None,
    search_context: str = ""
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

    location_instruction = ""
    if location:
        location_instruction = f"- The farmer is located in: {location}. When suggesting remedies or pesticides, explicitly mention that these commonly known treatments can be acquired at local agricultural shops in {location}. Do NOT refuse to answer due to lack of real-time store data; just give the widely known remedy names and tell them to check {location} markets.\n"

    prompt = f"""
You are an agricultural assistant for farmers.

STRICT RULES:
- You are an expert agronomist. NEVER refuse to answer claiming you lack real-time data or cannot prescribe pesticides.
- Be concise, practical, and farmer-friendly. Avoid scientific jargon.
- If the question is completely unrelated to farming or the disease, politely refuse by saying "I cannot answer this question".
{location_instruction}

CONTEXT:
Detected Disease: {disease} of cotton leaf
Confidence: {int(confidence * 100)}%

LOCAL MARKET SEARCH RESULTS:
{search_context if search_context else "No active web search results available."}

RECENT CONTEXT (last questions):
{history_block if history_block else "None"}

FARMER QUESTION:
{question}

CRITICAL RULES FOR YOUR ANSWER:
1. GIVE A DIRECT ANSWER IMMEDIATELY. NO intro phrases like "Sure," "Here is," or "Based on...". NO concluding phrases.
2. STICK TO THE FACTS. If asked for pesticides/brands: List ONLY the specific brands found in "LOCAL MARKET SEARCH RESULTS" and exactly how to use them.
3. If no search results are available, provide 2 generic widely-known brands and their usage.
4. MAXIMUM 2-3 SHORT LINES. Be extremely concise. Use simple farmer language.
5. Base your answer solely on the current question and local search results. Ignore history formatting.

ANSWER:
"""

    return prompt.strip()


def generate_answer(
    disease: str,
    confidence: float,
    last_qa: list,
    question: str,
    location: str = None,
    search_context: str = ""
) -> str:
    """
    Generates a safe answer using Gemma:2B.
    """
    try:
        prompt = build_prompt(
            disease=disease,
            confidence=confidence,
            last_qa=last_qa,
            question=question,
            location=location,
            search_context=search_context
        )

        print(f"Prompt built, sending to Ollama...")
        response = query_gemma(prompt)

        if not response:
            return (
                "I'm unable to answer that right now. "
                "Please consult an agriculture officer."
            )

        # Programmatically strip all markdown bolding/italics asterisks 
        # so the Text-to-Speech engine doesn't read them aloud.
        clean_response = response.strip().replace('*', '')

        return clean_response

    except Exception as e:
        print(f"Error in generate_answer: {e}")
        return "I'm having trouble answering right now. Please try again."

def generate_summary(qa_history: list, disease: str) -> str:
    """
    Generates a concise summary of the active session's conversation.
    """
    if not qa_history:
        return "No conversation to summarize."
        
    history_block = ""
    for qa in qa_history:
        q_text = qa.get("question_user") or qa.get("question", "")
        a_text = qa.get("answer_user") or qa.get("answer", "")
        history_block += f"Q: {q_text}\nA: {a_text}\n\n"
        
    prompt = f"""
You are an expert agricultural assistant summarizing a conversation with a farmer regarding the disease: {disease}.

CONVERSATION TRANSCRIPT:
{history_block}

YOUR TASK:
Create a very concise, direct summary of ONLY actionable advice. 
- Focus ONLY on: specific pesticide brands, application timings, dosage, or home remedies.
- NO introductory text. NO "This is a summary...".
- EXCLUDE questions where you refused to answer or engaged in small talk.
- If no advice was given, output: "No instructions discussed yet."
- Maximum 3-4 short bullet points. NO markdown asterisks (*).

SUMMARY:
"""
    try:
        response = query_gemma(prompt.strip())
        if not response:
            return "Failed to generate summary."
            
        clean_response = response.strip().replace('*', '')
        return clean_response
    except Exception as e:
        print(f"Error in generate_summary: {e}")
        return "Could not generate summary at this time."