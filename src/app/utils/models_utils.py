from app.core import settings
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr


gpt41_model = AzureChatOpenAI(
    api_key=SecretStr(settings.azure_api_key),
    azure_endpoint=settings.azure_endpoint,
    api_version="2025-01-01-preview",
    azure_deployment="gpt-4.1",
    name="gpt-4.1",
    temperature=0.1,
)
