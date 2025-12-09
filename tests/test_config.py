import pytest
from config import Config
import os
from unittest.mock import patch

class TestConfig:
    @patch.dict(os.environ, {
        "AZURE_SPEECH_KEY": "test_speech_key",
        "AZURE_SPEECH_REGION": "eastus",
        "USE_AZURE_OPENAI": "True",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test_openai_key",
        "AZURE_OPENAI_DEPLOYMENT": "test-deployment",
        "TEAMS_WEBHOOK_URL": "https://test.webhook.url",
        "SLACK_WEBHOOK_URL": "https://test.slack.url"
    })
    def test_validate_success(self):
        # We need to reload config or create a subclass since Config loads env vars at import time
        # However, Config methods read class attributes which are initialized at import.
        # We can mock the attributes directly for validation test.

        # Creating a subclass to override attributes for testing
        class TestConfigClass(Config):
            AZURE_SPEECH_KEY = "test_speech_key"
            AZURE_SPEECH_REGION = "eastus"
            USE_AZURE_OPENAI = True
            AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
            AZURE_OPENAI_API_KEY = "test_openai_key"
            AZURE_OPENAI_DEPLOYMENT = "test-deployment"
            TARGET_NAMES = ["Test"]

        missing = TestConfigClass.validate()
        assert len(missing) == 0

    def test_validate_missing(self):
        class TestConfigClass(Config):
            AZURE_SPEECH_KEY = ""
            AZURE_SPEECH_REGION = ""
            USE_AZURE_OPENAI = True
            AZURE_OPENAI_ENDPOINT = ""
            AZURE_OPENAI_API_KEY = ""
            AZURE_OPENAI_DEPLOYMENT = ""
            TARGET_NAMES = []

        missing = TestConfigClass.validate()
        assert "AZURE_SPEECH_KEY" in missing
        assert "AZURE_SPEECH_REGION" in missing
        assert "AZURE_OPENAI_ENDPOINT" in missing
        assert "AZURE_OPENAI_API_KEY" in missing
        assert "AZURE_OPENAI_DEPLOYMENT" in missing
        assert "TARGET_NAMES" in missing

    def test_print_config_masking(self, capsys):
        class TestConfigClass(Config):
            AZURE_SPEECH_KEY = "secret_key"
            AZURE_SPEECH_REGION = "eastus"
            USE_AZURE_OPENAI = True
            AZURE_OPENAI_DEPLOYMENT = "gpt-4"
            TEAMS_WEBHOOK_URL = "https://secret.url"
            SLACK_WEBHOOK_URL = ""
            TARGET_NAMES = ["Alice", "Bob"]
            FUZZ_THRESHOLD = 90
            ROLLING_BUFFER_MINUTES = 10
            SUMMARY_WINDOW_MINUTES = 5
            TRIGGER_COOLDOWN_SECONDS = 90
            OPENAI_MODEL = "gpt-3.5"

        TestConfigClass.print_config()
        captured = capsys.readouterr()

        # Check that secrets are NOT printed
        assert "secret_key" not in captured.out
        assert "https://secret.url" not in captured.out

        # Check that configuration status is printed
        assert "Teams Webhook: Configured" in captured.out
        assert "Slack Webhook: Not configured" in captured.out
        assert "Azure Speech Region: eastus" in captured.out
