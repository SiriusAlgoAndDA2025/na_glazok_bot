import base64
import logging
import os
from typing import Optional
from dataclasses import dataclass
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PromptResponse:
    prompt: str
    correct_answer: str  # "left", "right", "equal"
    explanation: str  # Explanation of why the answer is correct


class AIService:
    def __init__(self, api_key: str = None, base_url: str = None):
        # Use provided values or get from environment variables
        self.api_key = api_key or os.getenv('AI_API_KEY')
        self.base_url = (base_url or os.getenv('AI_BASE_URL', 'https://api.aitunnel.ru/v1')).rstrip('/')
        self.prompt_model = os.getenv('PROMPT_MODEL', 'deepseek-r1')
        self.image_model = os.getenv('IMAGE_MODEL', 'gpt-image-1-mini')

        if not self.api_key:
            raise ValueError('API key is required')

        # Configure OpenAI client
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        logger.info(f'[AIService] Initialized with base URL: {self.base_url}')
        logger.info(f'[AIService] Using prompt model: {self.prompt_model}')
        logger.info(f'[AIService] Using image model: {self.image_model}')

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def close(self):
        """Close the client (no-op for OpenAI)"""
        pass

    async def generate_prompt(self) -> PromptResponse:
        """Generate an optical illusion prompt with two objects"""
        logger.info(f'[AIService] Generating prompt with {self.prompt_model}')

        # First, randomly select the correct answer
        import random

        correct_answer = random.choice(['left', 'right', 'equal'])

        # Create a more specific prompt based on the correct answer
        if correct_answer == 'left':
            answer_description = 'the left object is actually larger'
        elif correct_answer == 'right':
            answer_description = 'the right object is actually larger'
        else:  # equal
            answer_description = 'they are actually equal'

        try:
            chat_result = await self.client.chat.completions.create(
                messages=[
                    {
                        'role': 'user',
                        'content': f'Create one optical illusion prompt with two objects where one appears larger than the other. The correct answer is \'{correct_answer}\' - this means: {answer_description}. They might be the same size but appear different due to context, or they might actually be different sizes. Respond with the prompt for image generation and a brief explanation in Russian of how the illusion works in JSON format like this: {{"prompt": "prompt text", "explanation": "brief explanation in Russian"}}. CRITICALLY IMPORTANT: The illusion must be designed so that the correct answer is true by actual pixel size, not just appearance. Examples: 1. Two central circles, left is larger and surrounded by smaller circles making it appear even larger (correct: left, explanation: left circle is actually larger and context enhances the difference). 2. Two rectangles, right is larger but with diverging lines making it appear smaller (correct: right, explanation: right rectangle is actually larger but perspective makes it appear smaller). 3. Two identical squares with symmetric surroundings (correct: equal, explanation: they are actually equal and appear equal).',
                    }
                ],
                model=self.prompt_model,
                max_tokens=50000,
            )

            content = chat_result.choices[0].message.content
            logger.info(f'[AIService] Received prompt response: {content}')

            # Clean up the content - remove markdown code block markers if present
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            elif content.startswith('```'):
                content = content[3:]  # Remove ```
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            content = content.strip()

            # Try to parse the JSON content from the AI response
            try:
                # Try to parse the entire content as JSON first
                import json

                json_content = json.loads(content)

                # Check if it's an array of objects
                if isinstance(json_content, list) and len(json_content) > 0:
                    # Use the first object from the array
                    json_content = json_content[0]

                prompt = json_content.get('prompt', '')
                # Use the predetermined correct answer instead of what the AI returns
                explanation = json_content.get('explanation', '')

                # If correctAnswer is not found, try "answer"
                if not correct_answer:
                    correct_answer = json_content.get('answer', 'equal')

            except json.JSONDecodeError:
                # If parsing fails, try to extract JSON from code block
                logger.warning('[AIService] Failed to parse JSON, trying to extract from code block')
                try:
                    # Try to find JSON in code block
                    start = content.find('{')
                    end = content.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        json_str = content[start : end + 1]
                        json_content = json.loads(json_str)

                        # Check if it's an array of objects
                        if isinstance(json_content, list) and len(json_content) > 0:
                            # Use the first object from the array
                            json_content = json_content[0]

                        prompt = json_content.get('prompt', '')
                        # Use the predetermined correct answer instead of what the AI returns
                        explanation = json_content.get('explanation', '')

                        # If correctAnswer is not found, try "answer"
                        if not correct_answer:
                            correct_answer = json_content.get('answer', 'equal')

                        logger.info('[AIService] Successfully extracted prompt and answer from code block')
                    else:
                        # If no JSON found, try to find a JSON-like pattern
                        import re

                        json_pattern = r'\{[^{}]*"prompt"[^{}]*"correctAnswer"[^{}]*\}'
                        match = re.search(json_pattern, content)
                        if match:
                            json_str = match.group()
                            json_content = json.loads(json_str)

                            # Check if it's an array of objects
                            if isinstance(json_content, list) and len(json_content) > 0:
                                # Use the first object from the array
                                json_content = json_content[0]

                            prompt = json_content.get('prompt', '')
                            # Use the predetermined correct answer instead of what the AI returns
                            explanation = json_content.get('explanation', '')
                            logger.info('[AIService] Successfully extracted prompt and answer using regex')
                        else:
                            # If no JSON found, use raw content
                            logger.warning('[AIService] No JSON found in response, using raw content')
                            prompt = content
                            correct_answer = 'equal'  # Default answer
                            explanation = ''  # Default explanation
                except Exception as e2:
                    # If all parsing fails, use raw content
                    logger.warning(f'[AIService] Failed to parse JSON from code block, using raw content: {str(e2)}')
                    prompt = content
                    correct_answer = 'equal'  # Default answer
                    explanation = ''  # Default explanation

            return PromptResponse(prompt=prompt, correct_answer=correct_answer, explanation=explanation)

        except Exception as e:
            logger.error(f'[AIService] Error generating prompt: {str(e)}')
            raise

    async def generate_image(self, prompt: str) -> str:
        """Generate an image based on a prompt"""
        logger.info(f'[AIService] Generating image with {self.image_model}')

        try:
            # Generate image
            result = await self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                quality=os.getenv('IMAGE_QUALITY', 'low'),
                size=os.getenv('IMAGE_SIZE', '1024x1024'),
                moderation=os.getenv('IMAGE_MODERATION', 'low'),
                output_format=os.getenv('IMAGE_FORMAT', 'png'),
            )

            image_base64 = result.data[0].b64_json
            logger.info(f'[AIService] Received image data, length: {len(image_base64) if image_base64 else 0}')
            return image_base64 or ''

        except Exception as e:
            logger.error(f'[AIService] Error generating image: {str(e)}')
            raise
