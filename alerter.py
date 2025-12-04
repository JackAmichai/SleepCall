"""
Alerter Module
Sends notifications via Teams, Slack, or desktop notifications
"""
import requests
from typing import Optional
from config import config

# Desktop notifications
try:
    from plyer import notification
    HAS_PLYER = True
except Exception:
    HAS_PLYER = False


class Alerter:
    """
    Sends alerts through multiple channels: Teams, Slack, and desktop notifications
    """
    
    def __init__(
        self,
        teams_webhook: str = None,
        slack_webhook: str = None,
        meeting_url: str = None
    ):
        """
        Initialize the alerter
        
        Args:
            teams_webhook: Teams incoming webhook URL (defaults to config)
            slack_webhook: Slack incoming webhook URL (defaults to config)
            meeting_url: Meeting join URL (defaults to config)
        """
        self.teams_webhook = teams_webhook or config.TEAMS_WEBHOOK_URL
        self.slack_webhook = slack_webhook or config.SLACK_WEBHOOK_URL
        self.meeting_url = meeting_url or config.MEETING_JOIN_URL
    
    def send_alert(self, summary: str, title: str = None) -> bool:
        """
        Send alert through all configured channels
        
        Args:
            summary: The summary text to send
            title: Optional custom title
            
        Returns:
            True if at least one alert was sent successfully
        """
        default_title = "👋 Your name was mentioned in the meeting"
        alert_title = title or default_title
        
        body = summary
        if self.meeting_url:
            body += f"\n\n🔗 Join meeting: {self.meeting_url}"
        
        success = False
        
        # Try Teams webhook
        if self._send_teams(alert_title, body):
            success = True
        
        # Try Slack webhook
        if self._send_slack(alert_title, body):
            success = True
        
        # Try desktop notification
        if self._send_desktop(alert_title, summary):
            success = True
        
        # Always log to console as fallback
        self._log_to_console(alert_title, summary)
        
        return success
    
    def _send_teams(self, title: str, body: str) -> bool:
        """Send alert to Microsoft Teams via webhook"""
        if not self.teams_webhook:
            return False
        
        try:
            payload = {
                "text": f"**{title}**\n\n{body}"
            }
            response = requests.post(
                self.teams_webhook,
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print("✓ Alert sent to Teams")
                return True
            else:
                print(f"✗ Teams webhook failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Teams webhook error: {e}")
            return False
    
    def _send_slack(self, title: str, body: str) -> bool:
        """Send alert to Slack via webhook"""
        if not self.slack_webhook:
            return False
        
        try:
            payload = {
                "text": f"*{title}*\n{body}"
            }
            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print("✓ Alert sent to Slack")
                return True
            else:
                print(f"✗ Slack webhook failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Slack webhook error: {e}")
            return False
    
    def _send_desktop(self, title: str, message: str) -> bool:
        """Send desktop notification"""
        if not HAS_PLYER:
            return False
        
        try:
            # Truncate message for desktop notification (max 240 chars)
            short_message = message[:240] + "..." if len(message) > 240 else message
            
            notification.notify(
                title=title,
                message=short_message,
                timeout=10
            )
            print("✓ Desktop notification sent")
            return True
        except Exception as e:
            print(f"✗ Desktop notification error: {e}")
            return False
    
    def _log_to_console(self, title: str, summary: str):
        """Log alert to console"""
        print("\n" + "=" * 50)
        print(f"🔔 {title}")
        print("=" * 50)
        print(summary)
        if self.meeting_url:
            print(f"\n🔗 Join: {self.meeting_url}")
        print("=" * 50 + "\n")
    
    def test_alert(self) -> dict:
        """
        Test all configured alert channels
        
        Returns:
            Dictionary with test results for each channel
        """
        results = {
            "teams": False,
            "slack": False,
            "desktop": False
        }
        
        test_title = "Test Alert from Meeting Sentinel"
        test_message = "This is a test notification. If you see this, alerts are working!"
        
        print("\n=== Testing Alert Channels ===")
        
        if self.teams_webhook:
            results["teams"] = self._send_teams(test_title, test_message)
        else:
            print("⊘ Teams webhook not configured")
        
        if self.slack_webhook:
            results["slack"] = self._send_slack(test_title, test_message)
        else:
            print("⊘ Slack webhook not configured")
        
        if HAS_PLYER:
            results["desktop"] = self._send_desktop(test_title, test_message)
        else:
            print("⊘ Desktop notifications not available (plyer not installed)")
        
        print("=" * 30 + "\n")
        
        return results
    
    def __repr__(self) -> str:
        channels = []
        if self.teams_webhook:
            channels.append("Teams")
        if self.slack_webhook:
            channels.append("Slack")
        if HAS_PLYER:
            channels.append("Desktop")
        
        return f"Alerter(channels={channels})"
