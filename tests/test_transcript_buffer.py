import pytest
from transcript_buffer import RollingTranscript
from datetime import datetime, timedelta, timezone
import time

class TestRollingTranscript:
    def test_add_and_get_entries(self):
        buffer = RollingTranscript(max_minutes=10)
        buffer.add("Speaker1", "Hello world")

        entries = buffer.get_entries()
        assert len(entries) == 1
        assert entries[0][1] == "Speaker1"
        assert entries[0][2] == "Hello world"

    def test_rolling_window(self):
        buffer = RollingTranscript(max_minutes=1)

        # Add old entry
        old_time = datetime.now(timezone.utc) - timedelta(minutes=2)
        buffer.add("OldSpeaker", "Old text", start_time_utc=old_time)

        # Add new entry
        new_time = datetime.now(timezone.utc)
        buffer.add("NewSpeaker", "New text", start_time_utc=new_time)

        entries = buffer.get_entries()
        assert len(entries) == 1
        assert entries[0][1] == "NewSpeaker"
        assert entries[0][2] == "New text"

    def test_last_minutes_text(self):
        buffer = RollingTranscript(max_minutes=10)
        now = datetime.now(timezone.utc)

        buffer.add("Speaker1", "Recent", start_time_utc=now)
        buffer.add("Speaker2", "Old", start_time_utc=now - timedelta(minutes=6))

        text = buffer.last_minutes_text(minutes=5)

        assert "Recent" in text
        assert "Old" not in text
        assert "Speaker1" in text

    def test_thread_safety(self):
        # Basic check to ensure no exceptions during concurrent access
        import threading

        buffer = RollingTranscript(max_minutes=10)

        def worker():
            for i in range(100):
                buffer.add(f"Speaker{i}", f"Text {i}")

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert buffer.size() == 500
