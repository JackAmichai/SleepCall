import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta
from meeting_processor import MeetingProcessor
from config import config

@pytest.fixture
def processor(mocker):
    # Mock Summarizer and Alerter
    mocker.patch('meeting_processor.Summarizer')
    mocker.patch('meeting_processor.Alerter')

    # Patch config BEFORE instantiation so NameDetector picks it up
    mocker.patch.object(config, 'TARGET_NAMES', ['Jack', 'Amichai'])
    mocker.patch.object(config, 'TRIGGER_COOLDOWN_SECONDS', 10)

    # Create processor instance
    proc = MeetingProcessor()

    # Mock internal components for control
    proc.summarizer.summarize.return_value = "Summary of the meeting."
    proc.alerter.send_alert.return_value = None

    return proc

def test_process_text_adds_to_buffer(processor):
    result = processor.process_text("Hello world", "Speaker 1")
    assert result["status"] == "processed"
    assert result["text"] == "Hello world"

    # Verify buffer content
    last_text = processor.buffer.last_minutes_text(1)
    assert "Hello world" in last_text

def test_name_detection_triggers_alert(processor):
    # Process text with target name
    result = processor.process_text("Hello Jack, how are you?", "Speaker 2")

    assert result["alert_sent"] is True
    assert result["summary"] == "Summary of the meeting."

    # Verify summarizer called
    processor.summarizer.summarize.assert_called_once()
    # Verify alerter called
    processor.alerter.send_alert.assert_called_once_with("Summary of the meeting.")

def test_cooldown_prevents_alert(processor):
    # First trigger
    processor.process_text("Hey Jack.", "Speaker 1")
    processor.summarizer.summarize.reset_mock()
    processor.alerter.send_alert.reset_mock()

    # Immediate second trigger
    result = processor.process_text("Jack, are you there?", "Speaker 1")

    assert result["alert_sent"] is False
    assert result.get("summary") is None

    processor.summarizer.summarize.assert_not_called()
    processor.alerter.send_alert.assert_not_called()

def test_alert_after_cooldown(processor, mocker):
    # First trigger
    processor.process_text("Hey Jack.", "Speaker 1")

    # Fast forward time
    processor.last_trigger_time = datetime.now(timezone.utc) - timedelta(seconds=20)

    # Reset mocks
    processor.summarizer.summarize.reset_mock()
    processor.alerter.send_alert.reset_mock()

    # Second trigger
    result = processor.process_text("Jack, are you there?", "Speaker 1")

    assert result["alert_sent"] is True
    processor.summarizer.summarize.assert_called_once()

def test_no_name_detected(processor):
    result = processor.process_text("Hello everyone.", "Speaker 1")
    assert result["alert_sent"] is False
    processor.summarizer.summarize.assert_not_called()
