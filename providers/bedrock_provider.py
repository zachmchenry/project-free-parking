"""
AWS Bedrock provider.

Bedrock hosts multiple model families (Anthropic Claude, Meta Llama,
Mistral, Cohere, Amazon Nova, etc.) behind a unified API. This sample
uses the Bedrock Converse API, which abstracts over model-specific
request shapes so the same code works for most hosted models.

Requires:
    pip install boto3
    AWS credentials configured (env vars, ~/.aws/credentials, or IAM role)

The model id is set via config.BEDROCK_MODEL_ID. Examples:
    'anthropic.claude-sonnet-4-5-v2:0'
    'meta.llama3-70b-instruct-v1:0'
    'amazon.nova-pro-v1:0'

Set AWS_REGION (defaults to us-east-1).
"""
import os
from typing import List, Dict

import boto3

from .base import LLMProvider
from config import BEDROCK_MODEL_ID


class BedrockProvider(LLMProvider):
    name = "bedrock"

    def __init__(self):
        self.model = BEDROCK_MODEL_ID
        region = os.environ.get("AWS_REGION", "us-east-1")
        # boto3 picks up credentials from env, ~/.aws/credentials, or IAM
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        # Bedrock Converse API uses {role, content: [{text: "..."}]} shape.
        bedrock_messages = [
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in messages
        ]
        response = self.client.converse(
            modelId=self.model,
            messages=bedrock_messages,
            system=[{"text": system}],
            inferenceConfig={
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        )
        # response shape: {"output": {"message": {"content": [{"text": "..."}]}}}
        content_blocks = response["output"]["message"]["content"]
        parts = [b.get("text", "") for b in content_blocks if "text" in b]
        return "".join(parts).strip()
