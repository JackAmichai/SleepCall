"""
Transcript Buffer Module
Maintains a rolling window of conversation transcripts with timestamps
"""
import threading
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional


class RollingTranscript:
    """
    Thread-safe rolling buffer for conversation transcripts.
    Automatically trims old entries based on configured time window.
    """
    
    def __init__(self, max_minutes: int = 10):
        """
        Initialize the rolling transcript buffer
        
        Args:
            max_minutes: Maximum minutes of transcript to retain
        """
        self.lines: deque = deque()
        self.max_minutes: int = max_minutes
        self.lock: threading.Lock = threading.Lock()
    
    def add(self, speaker: str, text: str, start_time_utc: Optional[datetime] = None):
        """
        Add a new transcript entry
        
        Args:
            speaker: Speaker identifier or name
            text: Transcribed text
            start_time_utc: UTC timestamp (defaults to current time)
        """
        if not text:
            return
        
        timestamp = start_time_utc or datetime.now(timezone.utc)
        
        with self.lock:
            self.lines.append((timestamp, speaker or "Unknown", text))
            self._trim_locked()
    
    def _trim_locked(self):
        """Remove entries older than max_minutes (must be called with lock held)"""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.max_minutes)
        while self.lines and self.lines[0][0] < cutoff:
            self.lines.popleft()
    
    def last_minutes_text(self, minutes: int = 5) -> str:
        """
        Get formatted transcript for the last N minutes
        
        Args:
            minutes: Number of minutes to retrieve
            
        Returns:
            Formatted transcript string with timestamps and speakers
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        with self.lock:
            selected = [
                f"[{ts.strftime('%H:%M:%S')}] {spk}: {txt}"
                for ts, spk, txt in self.lines
                if ts >= cutoff
            ]
        
        return "\n".join(selected) if selected else ""
    
    def get_entries(self, minutes: Optional[int] = None) -> List[Tuple[datetime, str, str]]:
        """
        Get raw transcript entries
        
        Args:
            minutes: Optional time window in minutes (None = all entries)
            
        Returns:
            List of (timestamp, speaker, text) tuples
        """
        with self.lock:
            if minutes is None:
                return list(self.lines)
            
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            return [(ts, spk, txt) for ts, spk, txt in self.lines if ts >= cutoff]
    
    def clear(self):
        """Clear all transcript entries"""
        with self.lock:
            self.lines.clear()
    
    def size(self) -> int:
        """Get number of entries in buffer"""
        with self.lock:
            return len(self.lines)
    
    def __len__(self) -> int:
        """Get number of entries in buffer"""
        return self.size()
    
    def __repr__(self) -> str:
        return f"RollingTranscript(entries={self.size()}, max_minutes={self.max_minutes})"
