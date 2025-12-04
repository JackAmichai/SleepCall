"""
Meeting Sentinel - Main Application
Real-time meeting transcription with name detection and instant alerts
"""
import time
import sys
from datetime import datetime, timezone, timedelta
import azure.cognitiveservices.speech as speechsdk

from config import config
from transcript_buffer import RollingTranscript
from name_detector import NameDetector
from summarizer import Summarizer
from alerter import Alerter


class MeetingSentinel:
    """
    Main application class that orchestrates real-time transcription,
    name detection, summarization, and alerting
    """
    
    def __init__(self):
        """Initialize the Meeting Sentinel"""
        # Validate configuration
        missing = config.validate()
        if missing:
            print("❌ Missing required configuration:")
            for item in missing:
                print(f"  - {item}")
            print("\nPlease set these in your .env file (see .env.example)")
            sys.exit(1)
        
        # Print configuration
        config.print_config()
        
        # Initialize components
        self.buffer = RollingTranscript(max_minutes=config.ROLLING_BUFFER_MINUTES)
        self.detector = NameDetector(
            target_names=config.TARGET_NAMES,
            fuzz_threshold=config.FUZZ_THRESHOLD
        )
        self.summarizer = Summarizer()
        self.alerter = Alerter()
        
        # Trigger cooldown tracking
        self.last_trigger_time = datetime.min.replace(tzinfo=timezone.utc)
        
        # Speech recognizer
        self.recognizer = None
        
        print("\n✓ Meeting Sentinel initialized successfully\n")
    
    def _should_trigger_alert(self) -> bool:
        """Check if enough time has passed since last trigger"""
        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_trigger_time).total_seconds()
        return elapsed >= config.TRIGGER_COOLDOWN_SECONDS
    
    def _handle_name_detected(self, text: str):
        """Handle name detection event"""
        if not self._should_trigger_alert():
            print(f"⏳ Cooldown active, skipping trigger (last alert was {int((datetime.now(timezone.utc) - self.last_trigger_time).total_seconds())}s ago)")
            return
        
        # Update last trigger time
        self.last_trigger_time = datetime.now(timezone.utc)
        
        # Get mentioned names
        mentioned = self.detector.find_mentioned_names(text)
        print(f"\n🎯 Name detected: {', '.join(mentioned)}")
        print(f"📝 In text: \"{text}\"")
        
        # Get recent transcript
        recent_text = self.buffer.last_minutes_text(config.SUMMARY_WINDOW_MINUTES)
        
        if not recent_text:
            print("⚠️  No recent transcript available for summary")
            return
        
        # Generate summary
        print(f"🤖 Generating summary of last {config.SUMMARY_WINDOW_MINUTES} minutes...")
        summary = self.summarizer.summarize(recent_text, mentioned)
        
        # Send alert
        print("📢 Sending alert...")
        self.alerter.send_alert(summary)
        
        print(f"✓ Alert sent! Next alert available in {config.TRIGGER_COOLDOWN_SECONDS}s\n")
    
    def _on_recognizing(self, evt: speechsdk.SpeechRecognitionEventArgs):
        """Handle intermediate recognition results (optional)"""
        # These are partial/interim results - can be noisy
        # Uncomment to see live transcription progress:
        # if evt.result.text:
        #     print(f"Recognizing: {evt.result.text}")
        pass
    
    def _on_recognized(self, evt: speechsdk.SpeechRecognitionEventArgs):
        """Handle final recognition results"""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text
            if not text:
                return
            
            # Timestamp (approximate - based on current time)
            timestamp = datetime.now(timezone.utc)
            speaker = "Speaker"  # Without diarization, we don't know who
            
            # Add to buffer
            self.buffer.add(speaker, text, timestamp)
            
            # Log transcript
            print(f"[{timestamp.strftime('%H:%M:%S')}] {speaker}: {text}")
            
            # Check for name detection
            if self.detector.is_name_mentioned(text):
                self._handle_name_detected(text)
        
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            # No speech recognized in this segment
            pass
    
    def _on_canceled(self, evt: speechsdk.SpeechRecognitionCanceledEventArgs):
        """Handle recognition cancellation"""
        print(f"\n❌ Recognition canceled: {evt.reason}")
        if evt.error_details:
            print(f"Error details: {evt.error_details}")
    
    def _on_session_started(self, evt):
        """Handle session start"""
        print("🎙️  Speech recognition session started")
        print("Listening for your name in the conversation...\n")
    
    def _on_session_stopped(self, evt):
        """Handle session stop"""
        print("\n⏹️  Speech recognition session stopped")
    
    def start(self):
        """Start the meeting sentinel"""
        try:
            # Configure Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=config.AZURE_SPEECH_KEY,
                region=config.AZURE_SPEECH_REGION
            )
            
            # Optional: Tune for better latency
            # speech_config.set_property(
            #     speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs,
            #     "300"
            # )
            
            # Audio configuration - using default microphone
            # To capture system audio, use a loopback device:
            # audio_config = speechsdk.audio.AudioConfig(device_name="DEVICE_ID")
            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            
            # Create recognizer
            self.recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Connect event handlers
            self.recognizer.recognizing.connect(self._on_recognizing)
            self.recognizer.recognized.connect(self._on_recognized)
            self.recognizer.canceled.connect(self._on_canceled)
            self.recognizer.session_started.connect(self._on_session_started)
            self.recognizer.session_stopped.connect(self._on_session_stopped)
            
            # Start continuous recognition
            print("🚀 Starting Meeting Sentinel...")
            print("Press Ctrl+C to stop\n")
            
            self.recognizer.start_continuous_recognition()
            
            # Keep running
            while True:
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping Meeting Sentinel...")
            if self.recognizer:
                self.recognizer.stop_continuous_recognition()
            print("✓ Stopped successfully")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if self.recognizer:
                self.recognizer.stop_continuous_recognition()
            sys.exit(1)
    
    def test_alerts(self):
        """Test alert functionality"""
        print("🧪 Testing alert system...\n")
        results = self.alerter.test_alert()
        
        success_count = sum(1 for v in results.values() if v)
        total_count = len([k for k, v in results.items() if v is not None])
        
        print(f"\nTest Results: {success_count}/{total_count} channels working")
        return results


def main():
    """Main entry point"""
    print("=" * 50)
    print("  Meeting Sentinel - Stay Focused, Never Miss Out")
    print("=" * 50)
    print()
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sentinel = MeetingSentinel()
        sentinel.test_alerts()
        return
    
    # Normal operation
    sentinel = MeetingSentinel()
    sentinel.start()


if __name__ == "__main__":
    main()
