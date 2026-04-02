from duckduckgo_search import DDGS

def get_pesticide_brands(disease: str, location: str) -> str:
    """
    Searches DuckDuckGo for locally available pesticide brands for a specific disease.
    Returns a consolidated string of text snippets to feed into the LLM context.
    """
    query = f"{disease} pesticide brands available in {location}, India for buying"
    
    try:
        results_context = ""
        with DDGS() as ddgs:
            # Fetch top 4 text snippets from web search
            results = ddgs.text(query, max_results=4)
            for r in results:
                body = r.get('body', '')
                if body:
                    results_context += f"- {body}\n"
                    
        print(f"[SEARCH] DuckDuckGo search successful for: '{query}'")
        return results_context
        
    except Exception as e:
        print(f"[SEARCH ERROR] Error fetching from DuckDuckGo: {e}")
        return ""
