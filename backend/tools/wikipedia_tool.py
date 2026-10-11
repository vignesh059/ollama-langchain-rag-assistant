"""
Built-in Wikipedia Search Tool for retrieving accurate article summaries and references.
"""

import wikipedia
from langchain_core.tools import tool

# Configure default wikipedia user agent to avoid HTTP 403 blocks
wikipedia.set_user_agent("ChatbotApp/1.0 (contact: user@example.com)")


@tool
def wikipedia_search_tool(query: str) -> str:
    """
    Use this tool to search Wikipedia for definitions, concepts, historical facts, people, places,
    or general information when the user asks 'search what it is' or requests information about a topic.
    
    Args:
        query (str): The search query or topic to search on Wikipedia.
    """
    try:
        # First attempt search to get relevant page titles
        search_results = wikipedia.search(query)
        if not search_results:
            return f"No Wikipedia results found for query: '{query}'."

        # Fetch summary of top result
        top_title = search_results[0]
        try:
            summary = wikipedia.summary(top_title, sentences=4, auto_suggest=False)
            page = wikipedia.page(top_title, auto_suggest=False)
            return (
                f"🌐 **Wikipedia Article: {page.title}**\n"
                f"**URL**: {page.url}\n\n"
                f"**Summary**:\n{summary}"
            )
        except wikipedia.DisambiguationError as de:
            # If disambiguation occurs, pick first option
            option = de.options[0] if de.options else query
            summary = wikipedia.summary(option, sentences=3, auto_suggest=False)
            return (
                f"🌐 **Wikipedia Topic: {option}** (Disambiguated from '{query}')\n\n"
                f"**Summary**:\n{summary}"
            )
        except wikipedia.PageError:
            return f"Could not find a specific Wikipedia page for '{query}'."

    except Exception as e:
        return f"Error querying Wikipedia tool: {str(e)}"
