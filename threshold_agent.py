from typing import Dict
from agno.agent import Agent
from agno.models.google import Gemini
from enum import Enum

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThresholdAgent:
    """Evaluates conditions and determines if alert notification is needed"""
    def __init__(self, gemini_key: str) -> None:
        self.agent = Agent(
            model=Gemini(
                id="gemini-2.5-flash",
                api_key=gemini_key
            ),
            markdown=True
        )

    def evaluate_alert_needed(self, aqi_data: Dict[str, float], hospital_plan: str, recommendations: str) -> tuple[bool, AlertLevel, str]:
        prompt = f"""
        You are a Threshold Evaluation Agent for a health alert system.
        Analyze the following data and determine if an SMS alert should be sent:
        **Air Quality Data:**
        - AQI: {aqi_data['aqi']} ({aqi_data['aqi_category']})
        - PM2.5: {aqi_data['pm25']} μg/m³
        - PM10: {aqi_data['pm10']} μg/m³
        **Hospital Planning Excerpt:**
        {hospital_plan[:500]}...
        **Health Recommendations Excerpt:**
        {recommendations[:500]}...
        **Alert Thresholds:**
        - CRITICAL: AQI > 200 OR Surge Risk = Critical OR Very Poor air quality with vulnerable populations
        - HIGH: AQI > 150 OR Surge Risk = High OR Poor air quality with health advisories
        - MEDIUM: AQI > 100 OR Surge Risk = Medium OR Moderate air quality concerns
        - LOW: No alert needed
        Respond in this EXACT format:
        ALERT_NEEDED: [YES/NO]
        ALERT_LEVEL: [CRITICAL/HIGH/MEDIUM/LOW]
        REASON: [Brief explanation in one sentence]
        """
        response = self.agent.run(prompt)
        content = response.content
        alert_needed = "YES" in content and "ALERT_NEEDED: YES" in content
        alert_level = AlertLevel.LOW
        if "CRITICAL" in content:
            alert_level = AlertLevel.CRITICAL
        elif "HIGH" in content:
            alert_level = AlertLevel.HIGH
        elif "MEDIUM" in content:
            alert_level = AlertLevel.MEDIUM
        reason = "Alert triggered based on air quality and health assessment."
        if "REASON:" in content:
            reason = content.split("REASON:")[1].split("\n")[0].strip()
        return alert_needed, alert_level, reason
