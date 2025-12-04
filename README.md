# SleepCall - Meeting Sentinel 🎯

**Never miss when your name is mentioned in a meeting!**

SleepCall is a real-time meeting assistant that listens to conversations, detects when your name is mentioned (similar to "Hey Google" or "Hey Siri"), and instantly alerts you with a concise summary of the last 5 minutes of the call—so you can join focused and ready to contribute.

---

## 🚀 Features

- **Real-time Speech Recognition**: Uses Azure Cognitive Services Speech SDK for accurate, low-latency transcription
- **Smart Name Detection**: Exact + fuzzy matching to catch your name even with accents or misspellings
- **Instant Summaries**: Azure OpenAI/OpenAI generates concise 5-minute summaries when your name is mentioned
- **Multi-channel Alerts**: Teams webhook, Slack webhook, and desktop notifications
- **Rolling Transcript Buffer**: Maintains a 10-minute rolling window of conversation history
- **Cooldown Protection**: Prevents alert spam with configurable cooldown periods
- **Easy Configuration**: Simple `.env` file setup

---

## 📋 Requirements

- **Python 3.8+**
- **Azure Cognitive Services Speech** subscription (get key + region)
- **Azure OpenAI** or **OpenAI API** key
- **Optional**: Teams or Slack webhook URL for alerts

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone git@github.com:JackAmichai/SleepCall.git
cd SleepCall
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example environment file:

```bash
copy .env.example .env  # Windows
# or
cp .env.example .env    # macOS/Linux
```

Edit `.env` and fill in your credentials:

```env
# Azure Speech Service (REQUIRED)
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=eastus

# Azure OpenAI (REQUIRED if USE_AZURE_OPENAI=True)
USE_AZURE_OPENAI=True
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# OR use OpenAI directly (set USE_AZURE_OPENAI=False)
# OPENAI_API_KEY=your_openai_key_here

# Target names to detect (comma-separated)
TARGET_NAMES=Jack,Amichai

# Alert webhooks (optional but recommended)
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

---

## 🎯 Usage

### Start Meeting Sentinel

```bash
python meeting_sentinel.py
```

The application will:
1. Start listening to your default microphone
2. Transcribe speech in real-time
3. Detect when your name is mentioned
4. Generate a 5-minute summary
5. Send alerts via Teams/Slack/desktop notification

### Test Alerts

```bash
python meeting_sentinel.py --test
```

This will send test notifications to all configured channels.

### Stop the Application

Press `Ctrl+C` to stop listening.

---

## 🏗️ Architecture

```
Audio Source  ──────────►  Azure Speech SDK  ─────────► Rolling Transcript Buffer
(microphone)              (Real-time STT)              (10-minute window)

                                                │
                                                ├─► Name Detection (exact + fuzzy)
                                                │
                                                └─► Trigger:
                                                       • Extract last 5 minutes
                                                       • Summarize with LLM
                                                       • Send alert (Teams/Slack/Desktop)
```

### Components

- **`config.py`**: Configuration management and validation
- **`transcript_buffer.py`**: Thread-safe rolling buffer for transcripts
- **`name_detector.py`**: Exact and fuzzy name matching
- **`summarizer.py`**: LLM-powered summarization (Azure OpenAI / OpenAI)
- **`alerter.py`**: Multi-channel notification system
- **`meeting_sentinel.py`**: Main application orchestration

---

## ⚙️ Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGET_NAMES` | `Jack,Amichai` | Comma-separated list of names to detect |
| `FUZZ_THRESHOLD` | `88` | Fuzzy matching threshold (0-100, higher = stricter) |
| `ROLLING_BUFFER_MINUTES` | `10` | Minutes of transcript to keep in memory |
| `SUMMARY_WINDOW_MINUTES` | `5` | Minutes to summarize when name is detected |
| `TRIGGER_COOLDOWN_SECONDS` | `90` | Cooldown between alerts to prevent spam |

---

## 🔧 Advanced Setup

### Capture System Audio (instead of microphone)

To listen to meeting audio from your speakers:

**Windows**: Install [VB-CABLE](https://vb-audio.com/Cable/) and configure as audio input

**macOS**: Install [BlackHole](https://github.com/ExistentialAudio/BlackHole) or Loopback

**Linux**: Use PulseAudio loopback module

Then modify `meeting_sentinel.py`:

```python
# Replace this line:
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# With:
audio_config = speechsdk.audio.AudioConfig(device_name="YOUR_LOOPBACK_DEVICE_ID")
```

### Speaker Diarization (Advanced)

To ignore when you say your own name, enable Azure Speech diarization or integrate [pyannote-audio](https://github.com/pyannote/pyannote-audio).

### Teams Bot Integration

For enterprise scenarios, deploy as a Microsoft Teams meeting bot using Graph API Real-Time Media to join meetings programmatically.

---

## 🔐 Security & Privacy

- **Consent**: Only use in meetings where you have permission to record/transcribe
- **Data Retention**: Transcripts are kept in memory only (configurable 10-minute window)
- **Encryption**: Consider encrypting any persisted logs
- **Compliance**: Ensure compliance with your organization's data governance policies

---

## 🐛 Troubleshooting

### "Missing required configuration" error
- Check that all required environment variables are set in `.env`
- Run `python meeting_sentinel.py --test` to verify alert setup

### No audio detected
- Verify microphone permissions
- Check that your microphone is set as default input device
- Test Azure Speech SDK with their sample code

### False positives/negatives
- Adjust `FUZZ_THRESHOLD` (88-92 works well for most cases)
- Add name variations to `TARGET_NAMES` (e.g., "Jack,Jacque,Jacques")

### Summary quality issues
- Ensure you have a valid OpenAI/Azure OpenAI API key
- Try a different model (e.g., `gpt-4` instead of `gpt-4o-mini`)

---

## 📚 Azure Resource Setup

### 1. Azure Speech Service

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a **Speech Service** resource
3. Get your **Key** and **Region**
4. Add to `.env` as `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`

### 2. Azure OpenAI

1. In Azure Portal, create an **Azure OpenAI** resource
2. Deploy a model (e.g., `gpt-4o-mini`, `gpt-4`)
3. Get your **Endpoint**, **API Key**, and **Deployment Name**
4. Add to `.env`

### 3. Teams Webhook

1. In Teams, go to the channel where you want alerts
2. Click **⋯** → **Connectors** → **Incoming Webhook**
3. Configure and copy the webhook URL
4. Add to `.env` as `TEAMS_WEBHOOK_URL`

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- Built with [Azure Cognitive Services Speech SDK](https://azure.microsoft.com/en-us/services/cognitive-services/speech-services/)
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) / [OpenAI](https://openai.com/)
- Fuzzy matching via [RapidFuzz](https://github.com/maxbachmann/RapidFuzz)
- Desktop notifications via [Plyer](https://github.com/kivy/plyer)

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review Azure Speech SDK documentation

---

**Stay focused. Never miss out. 🎯**
