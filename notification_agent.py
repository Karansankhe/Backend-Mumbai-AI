from typing import Dict
from enum import Enum

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

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

    def request_human_approval(self, alert_level: AlertLevel, reason: str, aqi_data: Dict[str, float]) -> bool:
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

    def send_sms(self, to_number: str, alert_level: AlertLevel, aqi_data: Dict[str, float], reason: str) -> bool:
        if not self.client:
            print("❌ Twilio client not initialized")
            return False
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

    def _format_alert_message(self, alert_level: AlertLevel, aqi_data: Dict[str, float], reason: str) -> str:
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
