"""
Meeting Sentinel - Main Application
Real-time meeting transcription with name detection and instant alerts
"""
import time
import sys
from datetime import datetime, timezone
import azure.cognitiveservices.speech as speechsdk

from config import config
from meeting_processor import MeetingProcessor
from alerter import Alerter # Still needed for direct testing


class MeetingSentinel:
    """
    Main application class that orchestrates real-time transcription
    and delegates processing to MeetingProcessor.
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
        
        # Initialize processor
        self.processor = MeetingProcessor()
        
        # Speech recognizer
        self.recognizer = None
        
        print("\n✓ Meeting Sentinel initialized successfully\n")
    
    def _on_recognizing(self, evt: speechsdk.SpeechRecognitionEventArgs):
        """Handle intermediate recognition results (optional)"""
        pass
    
    def _on_recognized(self, evt: speechsdk.SpeechRecognitionEventArgs):
        """Handle final recognition results"""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text
            timestamp = datetime.now(timezone.utc)
            speaker = "Speaker"
            
            # Log transcript
            print(f"[{timestamp.strftime('%H:%M:%S')}] {speaker}: {text}")
            
            # Process text using the processor
            result = self.processor.process_text(text, speaker)

            if result.get("alert_sent"):
                print(f"\n🎯 Name detected in: \"{text}\"")
                print("📢 Alert sent!")
                print(f"✓ Next alert available in {config.TRIGGER_COOLDOWN_SECONDS}s\n")
            elif result.get("text") and self.processor.detector.is_name_mentioned(result.get("text")):
                 # Name detected but cooldown active
                 # We need to access internal state to know if it was cooldown or empty buffer
                 # But for CLI output we can infer or add logging in processor
                 # For now, let's just leave it simple.
                 pass
        
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
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
        # We can access alerter through processor or create new one
        # Using processor's alerter ensures consistency
        results = self.processor.alerter.test_alert()
        
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
