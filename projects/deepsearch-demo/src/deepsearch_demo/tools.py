from tavily import TavilyClient
from dataclasses import dataclass
from langchain.tools import tool
from loguru import logger


@dataclass
class SearchResult:
    search_query: str
    title: str
    url: str
    content: str
    score: float | None = None


_tavily_client = None


@tool
def tavily_search(search_query: str) -> list[SearchResult]:
    """ """
    global _tavily_client
    if _tavily_client is None:
        try:
            _tavily_client = TavilyClient()
        except Exception:
            logger.exception('Environment variable `TAVILY_API_KEY` is required.')
            raise

    results = []
    try:
        response = _tavily_client.search(
            query=search_query,
            max_results=5,
            include_raw_content=True,
            timeout=240,
        )

        for item in response.get('results', []):
            result = SearchResult(
                search_query=search_query,
                title=item.get('title'),
                url=item.get('url'),
                content=item.get('content'),
                score=item.get('score'),
            )
            results.append(result)
    except Exception:
        logger.warning(f'Exception occurred while using tavily to query {search_query}')

    return results
