"""
Meeting Processor
Handles the core logic of processing meeting transcripts, detecting names,
and triggering summaries and alerts.
"""
from datetime import datetime, timezone
import logging

from config import config
from transcript_buffer import RollingTranscript
from name_detector import NameDetector
from summarizer import Summarizer
from alerter import Alerter

logger = logging.getLogger(__name__)

class MeetingProcessor:
    """
    Core logic for processing meeting text.
    Decoupled from input source (microphone, API, etc.)
    """
    def __init__(self):
        self.buffer = RollingTranscript(max_minutes=config.ROLLING_BUFFER_MINUTES)
        self.detector = NameDetector(
            target_names=config.TARGET_NAMES,
            fuzz_threshold=config.FUZZ_THRESHOLD
        )
        self.summarizer = Summarizer()
        self.alerter = Alerter()

        # Trigger cooldown tracking
        self.last_trigger_time = datetime.min.replace(tzinfo=timezone.utc)

    def process_text(self, text: str, speaker: str = "Speaker") -> dict:
        """
        Process a segment of text.
        Returns a dict with results of processing (e.g., if alert was sent).
        """
        if not text:
            return {"status": "empty"}

        timestamp = datetime.now(timezone.utc)

        # Add to buffer
        self.buffer.add(speaker, text, timestamp)

        result = {
            "status": "processed",
            "timestamp": timestamp.isoformat(),
            "text": text,
            "alert_sent": False
        }

        # Check for name detection
        if self.detector.is_name_mentioned(text):
            alert_result = self._handle_name_detected(text)
            if alert_result:
                result["alert_sent"] = True
                result["summary"] = alert_result

        return result

    def _should_trigger_alert(self) -> bool:
        """Check if enough time has passed since last trigger"""
        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_trigger_time).total_seconds()
        return elapsed >= config.TRIGGER_COOLDOWN_SECONDS

    def _handle_name_detected(self, text: str):
        """Handle name detection event. Returns summary if alert sent, else None."""
        if not self._should_trigger_alert():
            logger.info(f"Cooldown active, skipping trigger.")
            return None

        # Update last trigger time
        self.last_trigger_time = datetime.now(timezone.utc)

        # Get mentioned names
        mentioned = self.detector.find_mentioned_names(text)

        # Get recent transcript
        recent_text = self.buffer.last_minutes_text(config.SUMMARY_WINDOW_MINUTES)

        if not recent_text:
            logger.warning("No recent transcript available for summary")
            return None

        # Generate summary
        summary = self.summarizer.summarize(recent_text, mentioned)

        # Send alert
        self.alerter.send_alert(summary)

        return summary
