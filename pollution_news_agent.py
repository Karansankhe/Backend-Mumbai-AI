from typing import List, Optional
from dataclasses import dataclass
import http.client
import json

@dataclass
class NewsArticle:
    title: str
    snippet: str
    link: str
    date: Optional[str] = None

class PollutionNewsAgent:
    """Fetch and analyze pollution news using Serper API"""
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "google.serper.dev"

    def fetch_news(self, city: str, state: str, country: str) -> List[NewsArticle]:
        location = f"{city}"
        if state and state.lower() != 'none':
            location += f" {state}"
        queries = [
            f"{location} air pollution news",
            f"{state} pollution latest news" if state and state.lower() != 'none' else f"{country} pollution news",
            f"{location} air quality alert"
        ]
        all_articles = []
        for query in queries:
            try:
                conn = http.client.HTTPSConnection(self.base_url)
                payload = json.dumps({"q": query, "gl": country.lower()[:2], "tbs": "qdr:w", "num": 5})
                headers = {'X-API-KEY': self.api_key, 'Content-Type': 'application/json'}
                conn.request("POST", "/search", payload, headers)
                res = conn.getresponse()
                data = res.read()
                response_data = json.loads(data.decode("utf-8"))
                if 'organic' in response_data:
                    for result in response_data['organic'][:3]:
                        article = NewsArticle(
                            title=result.get('title', ''),
                            snippet=result.get('snippet', ''),
                            link=result.get('link', ''),
                            date=result.get('date', 'Recent')
                        )
                        all_articles.append(article)
                conn.close()
            except Exception:
                continue
        unique_articles = self._deduplicate_articles(all_articles)
        return unique_articles

    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        seen_titles = set()
        unique = []
        for article in articles:
            title_words = set(article.title.lower().split())
            title_fingerprint = frozenset(title_words)
            is_duplicate = False
            for seen in seen_titles:
                overlap = len(title_fingerprint & seen) / max(len(title_fingerprint), len(seen))
                if overlap > 0.6:
                    is_duplicate = True
                    break
            if not is_duplicate:
                seen_titles.add(title_fingerprint)
                unique.append(article)
        return unique

    def format_news_summary(self, articles: List[NewsArticle]) -> str:
        if not articles:
            return "No recent pollution news found for this location."
        summary = "**Recent Pollution News:**\n\n"
        for i, article in enumerate(articles, 1):
            summary += f"{i}. **{article.title}**\n   {article.snippet}\n   Date: {article.date}\n   Source: {article.link}\n\n"
        return summary
