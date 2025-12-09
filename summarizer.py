"""
Summarizer Module
Generates concise summaries of meeting transcripts using LLM
"""
from typing import List, Optional
from config import config


class Summarizer:
    """
    Creates summaries of conversation transcripts using Azure OpenAI or OpenAI
    """
    
    def __init__(
        self,
        use_azure: bool = None,
        azure_endpoint: str = None,
        azure_api_key: str = None,
        azure_deployment: str = None,
        openai_api_key: str = None,
        openai_model: str = None
    ):
        """
        Initialize the summarizer
        
        Args:
            use_azure: Whether to use Azure OpenAI (defaults to config)
            azure_endpoint: Azure OpenAI endpoint (defaults to config)
            azure_api_key: Azure OpenAI API key (defaults to config)
            azure_deployment: Azure OpenAI deployment name (defaults to config)
            openai_api_key: OpenAI API key (defaults to config)
            openai_model: OpenAI model name (defaults to config)
        """
        self.use_azure = use_azure if use_azure is not None else config.USE_AZURE_OPENAI
        self.azure_endpoint = azure_endpoint or config.AZURE_OPENAI_ENDPOINT
        self.azure_api_key = azure_api_key or config.AZURE_OPENAI_API_KEY
        self.azure_deployment = azure_deployment or config.AZURE_OPENAI_DEPLOYMENT
        self.openai_api_key = openai_api_key or config.OPENAI_API_KEY
        self.openai_model = openai_model or config.OPENAI_MODEL
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate OpenAI client"""
        try:
            if self.use_azure:
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=self.azure_api_key,
                    azure_endpoint=self.azure_endpoint,
                    api_version="2024-08-01-preview"
                )
            else:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_api_key)
        except Exception as e:
            # Avoid printing the full exception which might contain the API key
            print(f"Warning: Failed to initialize OpenAI client: {type(e).__name__}")
            self.client = None
    
    def summarize(
        self,
        transcript_text: str,
        target_names: Optional[List[str]] = None,
        max_words: int = 120
    ) -> str:
        """
        Generate a concise summary of the transcript
        
        Args:
            transcript_text: The transcript text to summarize
            target_names: Names that were mentioned (optional)
            max_words: Maximum words in summary
            
        Returns:
            Summary text
        """
        if not transcript_text or not transcript_text.strip():
            return "No recent conversation captured in the last 5 minutes."
        
        if not self.client:
            return "Summary unavailable: LLM client not initialized. Check your API keys."
        
        names_str = ", ".join(target_names) if target_names else ", ".join(config.TARGET_NAMES)
        
        system_prompt = (
            f"You are a concise meeting assistant. Summarize the last {config.SUMMARY_WINDOW_MINUTES} minutes "
            f"in <= {max_words} words, focusing on key points, decisions, and action items. "
            "If there are open questions or requests directed at the target person, highlight them. "
            "Be clear and actionable."
        )
        
        user_prompt = (
            f"Target person mentioned: {names_str}\n\n"
            f"Transcript (last {config.SUMMARY_WINDOW_MINUTES} minutes):\n"
            f"{transcript_text}\n\n"
            f"Provide a brief summary suitable for someone who needs to quickly join and contribute."
        )
        
        try:
            model_name = self.azure_deployment if self.use_azure else self.openai_model
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=220,
            )
            
            summary = response.choices[0].message.content.strip()
            return summary if summary else "Unable to generate summary from transcript."
            
        except Exception as e:
            # We log the type of error but avoid printing the full message which might contain keys
            print(f"Error in summarize: {type(e).__name__}")
            return f"(Summary unavailable: {type(e).__name__})"
    
    def __repr__(self) -> str:
        provider = "Azure OpenAI" if self.use_azure else "OpenAI"
        return f"Summarizer(provider={provider}, initialized={self.client is not None})"
