
from aqi_analyzer import AQIAnalyzer
from pollution_news_agent import PollutionNewsAgent, NewsArticle
from health_recommendation_agent import HealthRecommendationAgent, UserInput
from planning_agent import PlanningAgent
from threshold_agent import ThresholdAgent, AlertLevel
from notification_agent import NotificationAgent
import os
from dotenv import load_dotenv

load_dotenv()

# Example orchestrator function

def get_api_keys():
    return {
        "openweathermap": os.getenv("OPENWEATHERMAP_KEY"),
        "gemini": os.getenv("GEMINI_KEY"),
        "serper": os.getenv("SERPER_KEY")
    }

def get_notification_config():
    recipients = os.getenv("TWILIO_RECIPIENTS", "").split(",")
    return {
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
        "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
        "from_number": os.getenv("TWILIO_FROM_NUMBER"),
        "recipients": [r.strip() for r in recipients if r.strip()]
    }

def analyze_conditions(user_input, api_keys=None, healthcare_api_data=None, epidemic_signal=None, resource_status=None, notification_config=None):
    if api_keys is None:
        api_keys = get_api_keys()
    if notification_config is None:
        notification_config = get_notification_config()
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
    if alert_needed and notification_config and notification_config.get('account_sid'):
        notification_agent = NotificationAgent(
            account_sid=notification_config['account_sid'],
            auth_token=notification_config['auth_token'],
            from_number=notification_config['from_number']
        )
        if notification_agent.request_human_approval(alert_level, reason, aqi_data):
            for recipient in notification_config.get('recipients', []):
                notification_agent.send_sms(
                    to_number=recipient,
                    alert_level=alert_level,
                    aqi_data=aqi_data,
                    reason=reason
                )
    return recommendations, news_summary, hospital_plan, alert_needed, alert_level, reason
