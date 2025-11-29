from typing import Dict, List
from dataclasses import dataclass
from agno.agent import Agent
from agno.models.google import Gemini

@dataclass
class UserInput:
    city: str
    state: str
    country: str
    medical_conditions: str
    planned_activity: str

@dataclass
class NewsArticle:
    title: str
    snippet: str
    link: str
    date: str = None

class HealthRecommendationAgent:
    """Generate health recommendations using Gemini AI"""
    def __init__(self, gemini_key: str) -> None:
        self.agent = Agent(
            model=Gemini(
                id="gemini-2.5-flash",
                api_key=gemini_key
            ),
            markdown=True
        )

    def get_recommendations(self, aqi_data: Dict[str, float], user_input: UserInput, news_articles: List[NewsArticle]) -> str:
        prompt = self._create_prompt(aqi_data, user_input, news_articles)
        response = self.agent.run(prompt)
        return response.content

    def _create_prompt(self, aqi_data: Dict[str, float], user_input: UserInput, news_articles: List[NewsArticle]) -> str:
        location = f"{user_input.city}"
        if user_input.state and user_input.state.lower() != 'none':
            location += f", {user_input.state}"
        location += f", {user_input.country}"
        news_context = ""
        if news_articles:
            news_context = "\n**Recent News & Events:**\n"
            for article in news_articles[:5]:
                news_context += f"- {article.title}: {article.snippet}\n"
        else:
            news_context = "\n**Recent News:** No recent pollution alerts or news found.\n"
        return f"""
        Based on the following air quality, weather conditions, and recent pollution news in {location}:
        **Air Quality Data (as of {aqi_data['timestamp']}):**
        - Overall AQI: {aqi_data['aqi']} ({aqi_data['aqi_category']})
        - PM2.5 Level: {aqi_data['pm25']} µg/m³
        - PM10 Level: {aqi_data['pm10']} µg/m³
        - CO Level: {aqi_data['co']} µg/m³
        - NO2 Level: {aqi_data['no2']} µg/m³
        - O3 Level: {aqi_data['o3']} µg/m³
        - SO2 Level: {aqi_data['so2']} µg/m³
        **Weather Conditions:**
        - Temperature: {aqi_data['temperature']}°C
        - Humidity: {aqi_data['humidity']}%
        - Wind Speed: {aqi_data['wind_speed']:.2f} km/h
        {news_context}
        **User's Context:**
        - Medical Conditions: {user_input.medical_conditions or 'None reported'}
        - Planned Activity: {user_input.planned_activity}
        Please provide comprehensive, actionable health recommendations covering:
        1. **Current Situation Analysis**
        2. **Health Impact Assessment**
        3. **Activity Recommendations**
        4. **Safety Precautions**
        5. **Optimal Timing**
        6. **Risk Alerts**
        7. **Alternative Suggestions**
        8. **Long-term Awareness**
        Provide clear, practical advice that the user can immediately act upon.
        """
