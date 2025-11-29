
import streamlit as st
from typing import Dict, Optional, List
from dataclasses import dataclass
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
import requests
import http.client
import json
from datetime import datetime
from enum import Enum

# Streamlit UI Colors
COLORS = {
    "primary": "#1A2F64",
    "secondary": "#9CB5E8",
    "accent": "#E1E9FF",
    "white": "#FFFFFF"
}

# Streamlit UI Setup
st.set_page_config(page_title="AQI Health Analyzer", page_icon="🌍", layout="centered")
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {COLORS['accent']};
        }}
        .main-title {{
            color: {COLORS['primary']};
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
        }}
        .subtitle {{
            color: {COLORS['secondary']};
            font-size: 1.2rem;
            text-align: center;
        }}
        .stButton>button {{
            background-color: {COLORS['primary']};
            color: {COLORS['white']};
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">AQI Health Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Get air quality, health recommendations, and pollution news</div>', unsafe_allow_html=True)

with st.form("user_input_form"):
    city = st.text_input("City", "Delhi")
    state = st.text_input("State", "Delhi")
    country = st.text_input("Country", "India")
    medical_conditions = st.text_input("Medical Conditions (optional)")
    planned_activity = st.text_input("Planned Activity", "Morning walk")
    submitted = st.form_submit_button("Analyze")

if submitted:
    st.info("Analyzing conditions...", icon="🔎")
    # You can call analyze_conditions here and display results
    # st.write("Results will be shown here.")

# Define data structures
class AQIData(BaseModel):
    aqi: int = Field(description="Air Quality Index (1-5 scale)")
    pm25: float = Field(description="PM2.5 concentration (μg/m³)")
    pm10: float = Field(description="PM10 concentration (μg/m³)")
    co: float = Field(description="CO concentration (μg/m³)")
    no2: float = Field(description="NO2 concentration (μg/m³)")
    o3: float = Field(description="O3 concentration (μg/m³)")
    so2: float = Field(description="SO2 concentration (μg/m³)")
    timestamp: str = Field(description="Time when the data was recorded")

@dataclass
class UserInput:
    city: str
    state: str
    country: str
    medical_conditions: Optional[str]
    planned_activity: str

@dataclass
class NewsArticle:
    title: str
    snippet: str
    link: str
    date: Optional[str] = None

class AlertLevel(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AQIAnalyzer:
    """Fetch AQI and weather data using OpenWeatherMap API"""
    
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.base_air_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        self.base_weather_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def _get_coordinates(self, city: str, state: str, country: str) -> tuple:
        """Get latitude and longitude for the city"""
        if state and state.lower() != 'none':
            location_query = f"{city},{state},{country}"
        else:
            location_query = f"{city},{country}"
        
        print(f"\n🔍 Searching coordinates for: {location_query}")
        
        geo_url = f"{self.base_geo_url}?q={location_query}&limit=1&appid={self.api_key}"
        
        try:
            response = requests.get(geo_url, timeout=10)
            response.raise_for_status()
            
            geo_data = response.json()
            if not geo_data:
                raise ValueError(f"No coordinates found for {location_query}")
            
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            print(f"✓ Coordinates found: Lat={lat}, Lon={lon}")
            return lat, lon
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching coordinates: {str(e)}")
            raise
    
    def _convert_aqi_scale(self, aqi: int) -> int:
        """Convert OpenWeatherMap AQI (1-5) to US AQI scale (0-500)"""
        aqi_mapping = {
            1: 25,    # Good
            2: 75,    # Fair
            3: 125,   # Moderate
            4: 175,   # Poor
            5: 250    # Very Poor
        }
        return aqi_mapping.get(aqi, 0)
    
    def fetch_aqi_data(self, city: str, state: str, country: str) -> Dict[str, float]:
        """Fetch AQI and weather data from OpenWeatherMap"""
        try:
            lat, lon = self._get_coordinates(city, state, country)
            
            print(f"\n🌍 Fetching air quality data...")
            air_url = f"{self.base_air_url}?lat={lat}&lon={lon}&appid={self.api_key}"
            air_response = requests.get(air_url, timeout=10)
            air_response.raise_for_status()
            air_data = air_response.json()
            
            print(f"🌤️  Fetching weather data...")
            weather_url = f"{self.base_weather_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            weather_response = requests.get(weather_url, timeout=10)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            components = air_data['list'][0]['components']
            aqi_raw = air_data['list'][0]['main']['aqi']
            aqi_converted = self._convert_aqi_scale(aqi_raw)
            
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed'] * 3.6
            
            timestamp = datetime.fromtimestamp(air_data['list'][0]['dt']).strftime('%Y-%m-%d %H:%M:%S')
            
            result = {
                'aqi': aqi_converted,
                'aqi_category': self._get_aqi_category(aqi_raw),
                'temperature': temperature,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'pm25': components.get('pm2_5', 0),
                'pm10': components.get('pm10', 0),
                'co': components.get('co', 0),
                'no2': components.get('no2', 0),
                'o3': components.get('o3', 0),
                'so2': components.get('so2', 0),
                'timestamp': timestamp
            }
            
            print("\n📦 Extracted Data:")
            print(f"Timestamp: {result['timestamp']}")
            print(f"AQI: {result['aqi']} ({result['aqi_category']})")
            print(f"Temperature: {result['temperature']}°C")
            print(f"Humidity: {result['humidity']}%")
            print(f"Wind Speed: {result['wind_speed']:.2f} km/h")
            print(f"PM2.5: {result['pm25']} μg/m³")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error fetching AQI data: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'aqi': 0,
                'aqi_category': 'Unknown',
                'temperature': 0,
                'humidity': 0,
                'wind_speed': 0,
                'pm25': 0,
                'pm10': 0,
                'co': 0,
                'no2': 0,
                'o3': 0,
                'so2': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _get_aqi_category(self, aqi: int) -> str:
        """Get AQI category based on OpenWeatherMap scale"""
        categories = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        return categories.get(aqi, "Unknown")


class PollutionNewsAgent:
    """Fetch and analyze pollution news using Serper API"""
    
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "google.serper.dev"
    
    def fetch_news(self, city: str, state: str, country: str) -> List[NewsArticle]:
        """Fetch recent pollution news for the specified location"""
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
            print(f"\n📰 Fetching news for: {query}")
            
            try:
                conn = http.client.HTTPSConnection(self.base_url)
                
                payload = json.dumps({
                    "q": query,
                    "gl": country.lower()[:2],
                    "tbs": "qdr:w",
                    "num": 5
                })
                
                headers = {
                    'X-API-KEY': self.api_key,
                    'Content-Type': 'application/json'
                }
                
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
                        print(f"  ✓ Found: {article.title[:60]}...")
                
                conn.close()
                
            except Exception as e:
                print(f"  ❌ Error fetching news for '{query}': {str(e)}")
                continue
        
        unique_articles = self._deduplicate_articles(all_articles)
        print(f"\n✓ Total unique articles found: {len(unique_articles)}")
        return unique_articles
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
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
        """Format news articles into a readable summary"""
        if not articles:
            return "No recent pollution news found for this location."
        
        summary = "**Recent Pollution News:**\n\n"
        
        for i, article in enumerate(articles, 1):
            summary += f"{i}. **{article.title}**\n"
            summary += f"   {article.snippet}\n"
            summary += f"   Date: {article.date}\n"
            summary += f"   Source: {article.link}\n\n"
        
        return summary


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
    
    def get_recommendations(
        self,
        aqi_data: Dict[str, float],
        user_input: UserInput,
        news_articles: List[NewsArticle]
    ) -> str:
        """Generate personalized health recommendations with news context"""
        prompt = self._create_prompt(aqi_data, user_input, news_articles)
        response = self.agent.run(prompt)
        return response.content
    
    def _create_prompt(
        self, 
        aqi_data: Dict[str, float], 
        user_input: UserInput,
        news_articles: List[NewsArticle]
    ) -> str:
        """Create detailed prompt for health recommendations with news context"""
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
        
        1. **Current Situation Analysis**: Consider both the measured AQI data and any recent news/events that might affect air quality.
        
        2. **Health Impact Assessment**: Analyze how the current air quality affects general health and specifically address any medical conditions mentioned.
        
        3. **Activity Recommendations**: Evaluate the safety and advisability of the planned activity given current conditions.
        
        4. **Safety Precautions**: List specific protective measures (masks, timing, duration limits, indoor alternatives, etc.).
        
        5. **Optimal Timing**: Suggest the best time of day to conduct the activity based on typical pollution patterns.
        
        6. **Risk Alerts**: Highlight any immediate health risks or concerns.
        
        7. **Alternative Suggestions**: If conditions are unfavorable, suggest modifications or alternatives.
        
        8. **Long-term Awareness**: Mention any ongoing pollution issues or initiatives from the news.
        
        Provide clear, practical advice that the user can immediately act upon.
        """


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
    
    def create_plan(
        self,
        aqi_data: Dict[str, float],
        news_summary: str,
        healthcare_api_data: Dict,
        epidemic_signal: Optional[Dict] = None,
        resource_status: Optional[Dict] = None
    ) -> str:
        """Generate planning actions for hospitals"""
        prompt = self._build_prompt(aqi_data, news_summary, healthcare_api_data, epidemic_signal, resource_status)
        response = self.agent.run(prompt)
        return response.content
    
    def _build_prompt(
        self,
        aqi_data: Dict[str, float],
        news_summary: str,
        healthcare_api_data: Dict,
        epidemic_signal: Optional[Dict],
        resource_status: Optional[Dict]
    ) -> str:
        epidemic_context = json.dumps(epidemic_signal or {"status": "No epidemic risk passed"})
        resource_context = json.dumps(resource_status or {"status": "No hospital resource data passed"})
        healthcare_context = json.dumps(healthcare_api_data or {"status": "No healthcare API data shared yet"})
        
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
        
        🧾 **Healthcare API Sample Data**
        {healthcare_context}
        
        ---
        
        Using this available data, generate a **realistic actionable hospital planning response** including:
        
        1. **Surge Risk Level**
           - Low / Medium / High / Critical (justified from input data)
           
        2. **Patient Load Forecast**
           - Expected additional patients (percentage or absolute from signals)
           
        3. **Staffing Plan**
           - Doctors, Nurses, Emergency staff adjustments
           - Shift increase or optimized movement across departments
           
        4. **Equipment & Supplies**
           - Oxygen, masks, emergency beds, ICU buffer, nebulizers if asthma risk
           
        5. **Air + Epidemic Precautions**
           - Mandatory masks, indoor crowd control, ventilation timing if pollution crisis
           
        6. **Capacity Optimization**
           - Add/remove departments from priority, redirect non-urgent cases
           
        7. **Festival / Crowd Logistics (if any epidemic signal supports surge)**
           - Staffing mobility plan, ambulance availability, ER standby
           
        8. **Plan Summary**
           - Bullet actionable checklist hospitals can implement immediately
        
        **IMPORTANT:** End your response with a clear surge risk classification in this exact format:
        SURGE_RISK_LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
        """


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
    
    def evaluate_alert_needed(
        self,
        aqi_data: Dict[str, float],
        hospital_plan: str,
        recommendations: str
    ) -> tuple[bool, AlertLevel, str]:
        """
        Evaluate if alert notification is needed based on conditions
        Returns: (should_alert, alert_level, reason)
        """
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
        
        # Parse response
        alert_needed = "YES" in content and "ALERT_NEEDED: YES" in content
        
        # Determine alert level
        alert_level = AlertLevel.LOW
        if "CRITICAL" in content:
            alert_level = AlertLevel.CRITICAL
        elif "HIGH" in content:
            alert_level = AlertLevel.HIGH
        elif "MEDIUM" in content:
            alert_level = AlertLevel.MEDIUM
        
        # Extract reason
        reason = "Alert triggered based on air quality and health assessment."
        if "REASON:" in content:
            reason = content.split("REASON:")[1].split("\n")[0].strip()
        
        return alert_needed, alert_level, reason


class NotificationAgent:
    """Handles SMS notifications via Twilio with human-in-the-loop approval"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        try:
            from twilio.rest import Client
            self.client = Client(account_sid, auth_token)
            self.from_number = from_number
        except ImportError:
            print("⚠️  Twilio library not installed. Install with: pip install twilio")
            self.client = None
    
    def request_human_approval(
        self,
        alert_level: AlertLevel,
        reason: str,
        aqi_data: Dict[str, float]
    ) -> bool:
        """Ask for human approval before sending notification"""
        print(f"\n{'='*60}")
        print("🚨 ALERT NOTIFICATION REQUEST")
        print(f"{'='*60}")
        print(f"Alert Level: {alert_level.value.upper()}")
        print(f"Reason: {reason}")
        print(f"AQI: {aqi_data['aqi']} ({aqi_data['aqi_category']})")
        print(f"PM2.5: {aqi_data['pm25']} μg/m³")
        print(f"{'='*60}")
        
        while True:
            response = input("\n📲 Do you want to send SMS notification? (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                print("❌ Notification cancelled by user.")
                return False
            else:
                print("Please enter 'yes' or 'no'")
    
    def send_sms(
        self,
        to_number: str,
        alert_level: AlertLevel,
        aqi_data: Dict[str, float],
        reason: str
    ) -> bool:
        """Send SMS notification via Twilio"""
        if not self.client:
            print("❌ Twilio client not initialized")
            return False
        
        # Create message content
        message_body = self._format_alert_message(alert_level, aqi_data, reason)
        
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_number
            )
            print(f"✅ SMS sent successfully! SID: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error sending SMS: {str(e)}")
            return False
    
    def _format_alert_message(
        self,
        alert_level: AlertLevel,
        aqi_data: Dict[str, float],
        reason: str
    ) -> str:
        """Format alert message for SMS"""
        emoji_map = {
            AlertLevel.CRITICAL: "🔴",
            AlertLevel.HIGH: "🟠",
            AlertLevel.MEDIUM: "🟡",
            AlertLevel.LOW: "🟢"
        }
        
        emoji = emoji_map.get(alert_level, "⚠️")
        
        message = f"{emoji} HEALTH ALERT - {alert_level.value.upper()}\n\n"
        message += f"AQI: {aqi_data['aqi']} ({aqi_data['aqi_category']})\n"
        message += f"PM2.5: {aqi_data['pm25']} μg/m³\n\n"
        message += f"{reason}\n\n"
        message += "Take necessary precautions. Check full report for details."
        
        return message


def analyze_conditions(
    user_input: UserInput,
    api_keys: Dict[str, str],
    healthcare_api_data: Optional[Dict] = None,
    epidemic_signal: Optional[Dict] = None,
    resource_status: Optional[Dict] = None,
    notification_config: Optional[Dict] = None
) -> tuple:
    """Main function to analyze conditions and generate recommendations"""
    
    print(f"\n{'='*60}")
    print(f"🏥 AQI Health Analyzer with News Intelligence")
    print(f"{'='*60}")
    
    # Initialize components
    aqi_analyzer = AQIAnalyzer(api_key=api_keys['openweathermap'])
    news_agent = PollutionNewsAgent(api_key=api_keys['serper'])
    health_agent = HealthRecommendationAgent(gemini_key=api_keys['gemini'])
    planning_agent = PlanningAgent(gemini_key=api_keys['gemini'])
    threshold_agent = ThresholdAgent(gemini_key=api_keys['gemini'])
    
    # Fetch AQI data
    aqi_data = aqi_analyzer.fetch_aqi_data(
        city=user_input.city,
        state=user_input.state,
        country=user_input.country
    )
    
    # Fetch pollution news
    news_articles = news_agent.fetch_news(
        city=user_input.city,
        state=user_input.state,
        country=user_input.country
    )
    
    # Generate health recommendations
    print(f"\n🤖 Generating health recommendations with news context...")
    recommendations = health_agent.get_recommendations(
        aqi_data, 
        user_input, 
        news_articles
    )
    
    # Format news summary
    news_summary = news_agent.format_news_summary(news_articles)
    
    # Generate hospital planning
    print(f"\n📊 Generating hospital planning actions...")
    hospital_plan = planning_agent.create_plan(
        aqi_data,
        news_summary,
        healthcare_api_data or {},
        epidemic_signal,
        resource_status
    )
    
    # Evaluate if notification is needed
    print(f"\n🔍 Evaluating alert thresholds...")
    alert_needed, alert_level, reason = threshold_agent.evaluate_alert_needed(
        aqi_data,
        hospital_plan,
        recommendations
    )
    
    # Handle notification if needed and configured
    if alert_needed and notification_config:
        print(f"\n⚠️  Alert condition detected: {alert_level.value.upper()}")
        
        notification_agent = NotificationAgent(
            account_sid=notification_config['account_sid'],
            auth_token=notification_config['auth_token'],
            from_number=notification_config['from_number']
        )
        
        # Request human approval
        if notification_agent.request_human_approval(alert_level, reason, aqi_data):
            # Send SMS to configured recipients
            for recipient in notification_config.get('recipients', []):
                notification_agent.send_sms(
                    to_number=recipient,
                    alert_level=alert_level,
                    aqi_data=aqi_data,
                    reason=reason
                )
        else:
            print("ℹ️  Notification skipped by user.")
    elif alert_needed:
        print(f"\n⚠️  Alert condition detected but notification config not provided")
    else:
        print(f"\n✅ No alert needed - conditions are within acceptable thresholds")
    
    return recommendations, news_summary, hospital_plan


# ---------- Console Execution Example ----------
if __name__ == "__main__":
    
    # API Keys Configuration
    API_KEYS = {
        "openweathermap": "292636889da2b86ced52a4bb723f9ec3",
        "gemini": "AIzaSyAFu4X9s56NHqHHRZ-EkvEeArAniqk-l_E",
        "serper": "2e4050bdeb4fdbc9f8783278ff56995659488db8"
    }
    
    # Twilio Notification Configuration (Optional)
    NOTIFICATION_CONFIG = {
        "account_sid": "AC598bb2970cf99031bfdcefe03a6e1800",
        "auth_token": "5aa7f276e91b0fe66b981da127ae5df5",
        "from_number": "+12403346256",
        "recipients": [
            "+919082222597",
            "+917517456501"
            # Add your phone numbers here
            
        ]
    }
    try:
        # Example user input (replace with real input or prompt the user)
        user_input = UserInput(
            city="Los Angeles",
            state="CA",
            country="USA",
            medical_conditions=None,
            planned_activity="Outdoor exercise"
        )

        # Run analysis with notification support
        recommendations, news_summary, hospital_plan = analyze_conditions(
            user_input=user_input,
            api_keys=API_KEYS,
            healthcare_api_data={"sample": "data"},
            epidemic_signal={"risk_level": "low"},
            resource_status={"beds_available": 150},
            notification_config=NOTIFICATION_CONFIG  # Pass None to disable notifications
        )
        
        print(f"\n{'='*60}")
        print("📰 RECENT POLLUTION NEWS")
        print(f"{'='*60}\n")
        print(news_summary)
        
        print(f"\n{'='*60}")
        print("✅ HEALTH RECOMMENDATIONS")
        print(f"{'='*60}\n")
        print(recommendations)
        
        print(f"\n{'='*60}")
        print("🏥 HOSPITAL PLANNING ACTIONS")
        print(f"{'='*60}\n")
        print(hospital_plan)
        
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()