import pytest
from unittest.mock import MagicMock, patch
from summarizer import Summarizer

class TestSummarizer:
    @patch("summarizer.config")
    def test_summarize_success(self, mock_config):
        # Setup mocks
        mock_config.SUMMARY_WINDOW_MINUTES = 5
        mock_config.TARGET_NAMES = ["Jack"]

        summarizer = Summarizer(
            use_azure=False,
            openai_api_key="test_key"
        )

        # Mock the client
        summarizer.client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This is a summary."
        summarizer.client.chat.completions.create.return_value = mock_response

        summary = summarizer.summarize("Transcript text")

        assert summary == "This is a summary."
        summarizer.client.chat.completions.create.assert_called_once()

    def test_summarize_no_client(self):
        summarizer = Summarizer(use_azure=False)
        summarizer.client = None # Force no client

        summary = summarizer.summarize("Transcript text")
        assert "LLM client not initialized" in summary

    def test_summarize_empty_transcript(self):
        summarizer = Summarizer(use_azure=False, openai_api_key="test")
        summarizer.client = MagicMock()

        summary = summarizer.summarize("")
        assert "No recent conversation" in summary

    @patch("summarizer.config")
    def test_summarize_exception_handling(self, mock_config):
        summarizer = Summarizer(use_azure=False, openai_api_key="test")
        summarizer.client = MagicMock()
        summarizer.client.chat.completions.create.side_effect = Exception("API Error")

        summary = summarizer.summarize("Transcript text")
        assert "Summary unavailable" in summary
        # Ensure the error message in the return value doesn't contain raw sensitive info if we can avoid it,
        # but our implementation logs type(e).__name__.
        assert "Exception" in summary
