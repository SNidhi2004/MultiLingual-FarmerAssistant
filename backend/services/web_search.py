from duckduckgo_search import DDGS

def get_pesticide_brands(disease: str, location: str) -> str:
    """
    Searches DuckDuckGo for locally available pesticide brands for a specific disease.
    Returns a consolidated string of text snippets to feed into the LLM context.
    """
    query = f"{disease} pesticide brands available in {location}, India for buying"
    
    try:
        results_context = ""
        # The latest version of DDGS is more robust when used without a context manager in some environments
        ddgs = DDGS()
        results = ddgs.text(query, max_results=4)
        
        if results:
            for r in results:
                body = r.get('body', '')
                if body:
                    results_context += f"- {body}\n"
                    
            print(f"[SEARCH] DuckDuckGo search successful for: '{query}'")
        else:
            print(f"[SEARCH] No results found for: '{query}'")
            
        return results_context
        
    except Exception as e:
        print(f"[SEARCH ERROR] Connection to DuckDuckGo/Bing failed (Expected on some Azure regions): {e}")
        return ""
