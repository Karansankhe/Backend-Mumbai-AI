import os
from aqi_analyzer import AQIAnalyzer
from pollution_news_agent import PollutionNewsAgent, NewsArticle
from health_recommendation_agent import HealthRecommendationAgent, UserInput
from planning_agent import PlanningAgent
from threshold_agent import ThresholdAgent, AlertLevel


def get_api_keys():
    # Replace the following with actual logic to retrieve API keys
    return {
        'openweathermap': os.getenv("OPENWEATHERMAP_KEY"),
        'serper': os.getenv("SERPER_KEY"),
        'gemini': os.getenv("GEMINI_KEY")
    }

# Example orchestrator function

def analyze_conditions(user_input, api_keys=None, healthcare_api_data=None, epidemic_signal=None, resource_status=None):
    if api_keys is None:
        api_keys = get_api_keys()
    aqi_analyzer = AQIAnalyzer(api_key=api_keys['openweathermap'])
    news_agent = PollutionNewsAgent(api_key=api_keys['serper'])
    health_agent = HealthRecommendationAgent(gemini_key=api_keys['gemini'])
    planning_agent = PlanningAgent(gemini_key=api_keys['gemini'])
    threshold_agent = ThresholdAgent(gemini_key=api_keys['gemini'])
    aqi_data = aqi_analyzer.fetch_aqi_data(
        city=user_input.city,
        state=user_input.state,
        country=user_input.country
    )
    news_articles = news_agent.fetch_news(
        city=user_input.city,
        state=user_input.state,
        country=user_input.country
    )
    recommendations = health_agent.get_recommendations(
        aqi_data,
        user_input,
        news_articles
    )
    news_summary = news_agent.format_news_summary(news_articles)
    hospital_plan = planning_agent.create_plan(
        aqi_data,
        news_summary,
        healthcare_api_data or {},
        epidemic_signal,
        resource_status,
        state=user_input.state
    )
    alert_needed, alert_level, reason = threshold_agent.evaluate_alert_needed(
        aqi_data,
        hospital_plan,
        recommendations
    )
    return recommendations, news_summary, hospital_plan, alert_needed, alert_level, reason

