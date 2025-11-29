from typing import Dict, Optional
from agno.agent import Agent
from agno.models.google import Gemini
import json
# Import hospital resource data
from hospital_resources import get_hospital_count, get_resource_breakdown

class PlanningAgent:
    """Creates hospital planning decisions based on multi-agent data inputs"""
    def __init__(self, gemini_key: str) -> None:
        self.agent = Agent(
            model=Gemini(
                id="gemini-2.5-flash",
                api_key=gemini_key
            ),
            markdown=True
        )

    def create_plan(self, aqi_data: Dict[str, float], news_summary: str, healthcare_api_data: Dict, epidemic_signal: Optional[Dict] = None, resource_status: Optional[Dict] = None, state: Optional[str] = None) -> str:
        # Get hospital resource info for the state/UT
        hospital_info = get_hospital_count(state or "") if state else None
        bed_info = get_resource_breakdown("Bed Strength")
        doctor_info = get_resource_breakdown("Number of Doctors")
        nurse_info = get_resource_breakdown("Number of Nurses")
        prompt = self._build_prompt(aqi_data, news_summary, healthcare_api_data, epidemic_signal, resource_status, hospital_info, bed_info, doctor_info, nurse_info)
        response = self.agent.run(prompt)
        return response.content

    def _build_prompt(self, aqi_data: Dict[str, float], news_summary: str, healthcare_api_data: Dict, epidemic_signal: Optional[Dict], resource_status: Optional[Dict], hospital_info=None, bed_info=None, doctor_info=None, nurse_info=None) -> str:
        epidemic_context = json.dumps(epidemic_signal or {"status": "No epidemic risk passed"})
        resource_context = json.dumps(resource_status or {"status": "No hospital resource data passed"})
        healthcare_context = json.dumps(healthcare_api_data or {"status": "No healthcare API data shared yet"})
        # Format hospital resource info
        hospital_resource_text = ""
        if hospital_info:
            hospital_resource_text += f"\n🏥 **State/UT Hospital Resources**\n- Public Hospitals: {hospital_info.get('Number of hospitals in public sector', 'NA')}\n- Private Hospitals: {hospital_info.get('Number of hospitals in private sector', 'NA')}\n- Total Hospitals: {hospital_info.get('Total number of hospitals (public+private)', 'NA')}\n"
        if bed_info:
            hospital_resource_text += f"- Total Bed Strength: {bed_info.get('Total', 'NA')}\n"
        if doctor_info:
            hospital_resource_text += f"- Total Doctors: {doctor_info.get('Total', 'NA')}\n"
        if nurse_info:
            hospital_resource_text += f"- Total Nurses: {nurse_info.get('Total', 'NA')}\n"
        return f"""
        You are a **Hospital Planning Agent for surge preparedness**.
        **Inputs received from other agents:**
        📌 **Air Quality & Weather**
        - AQI: {aqi_data['aqi']} ({aqi_data['aqi_category']})
        - PM2.5: {aqi_data['pm25']} μg/m³
        - PM10: {aqi_data['pm10']} μg/m³
        - Temperature: {aqi_data['temperature']}°C
        - Humidity: {aqi_data['humidity']}%
        - Wind Speed: {aqi_data['wind_speed']:.2f} km/h
        📰 **Pollution / Local News Summary**
        {news_summary}
        🧬 **Epidemic Risk Signal**
        {epidemic_context}
        🏥 **Hospital Resource Status**
        {resource_context}
        {hospital_resource_text}
        🧾 **Healthcare API Sample Data**
        {healthcare_context}
        ---
        Using this available data, generate a **realistic actionable hospital planning response** including:
        1. **Surge Risk Level**
        2. **Patient Load Forecast**
        3. **Staffing Plan**
        4. **Equipment & Supplies**
        5. **Air + Epidemic Precautions**
        6. **Capacity Optimization**
        7. **Festival / Crowd Logistics**
        8. **Resource Allocation Recommendations** (suggest which facilities/resources to use based on situation)
        9. **Plan Summary**
        **IMPORTANT:** End your response with a clear surge risk classification in this exact format:
        SURGE_RISK_LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
        """
