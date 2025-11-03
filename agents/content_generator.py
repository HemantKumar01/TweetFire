#!/usr/bin/env python3
import os
from llama_index.llms.google_genai import GoogleGenAI
from dotenv import load_dotenv

load_dotenv()


class ContentGenerator:
    def __init__(self):
        self.llm = GoogleGenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            model="gemini-2.5-flash",
        )

    async def generate_twitter_post(
        self, trending_topic: str, description: str = "", category: str = ""
    ) -> str:
        """Generate a Twitter post based on trending topic"""
        prompt = f"""{trending_topic} is trending now. Create a trendy, cringe post about droidrun relating to it. This post needs to be posted on twitter, and it should be less than 250 characters long. It should not sound like an advertisement. it should start with a small clickbait story, but a twist should come and it should be reach gracefully about droidrun at end. 
        
        category: {category}
        
        About Droidrun
          DroidRun is a powerful framework for controlling Android and iOS devices through LLM agents. It allows you to automate device interactions using natural language commands. Droidrun is the topmost android use agent according to android world benchmark 
          Why Droidrun?
            🤖 Control Android and iOS devices with natural language commands 
            🔀 Supports multiple LLM providers (OpenAI, Anthropic, Gemini, Ollama, DeepSeek) 
            🧠 Planning capabilities for complex multi-step tasks 
            💻 Easy to use CLI with enhanced debugging features 
            🐍 Extendable Python API for custom automations 
            📸 Screenshot analysis for visual understanding of the device 
            🫆 Execution tracing with Arize Phoenix
        
        Requirements:
        - Keep it under 250 characters
        - Emojis are considered of 2 character length
        - Make it engaging and shareable
        - Include relevant hashtags (2-3 max)
        - Use trending/popular tone
        - Don't include quotes around the final output
        

        Make sure the tweet is strictly less than 250 characters.
        Return only the tweet content, nothing else.
        """

        response = await self.llm.acomplete(prompt)
        return response.text.strip()

    async def generate_image_prompt(
        self, trending_topic: str, twitter_post: str
    ) -> str:
        """Generate an image prompt for the trending topic"""
        prompt = f"""{trending_topic} is trending now. Create a trendy clickbait image prompt about it for AI image generator. This image needs to be posted on twitter. It should not look like an advertisement, it would be better if it is some illustration, comic or drawing. For context the text captions to be posted with the image is:
        {twitter_post}
        
        About Droidrun
          DroidRun is a powerful framework for controlling Android and iOS devices through LLM agents. It allows you to automate device interactions using natural language commands. Droidrun is the topmost android usee agent according to android world benchmark 
          Why Droidrun?
            🤖 Control Android and iOS devices with natural language commands 
            🔀 Supports multiple LLM providers (OpenAI, Anthropic, Gemini, Ollama, DeepSeek) 
            🧠 Planning capabilities for complex multi-step tasks 
            💻 Easy to use CLI with enhanced debugging features 
            🐍 Extendable Python API for custom automations 
            📸 Screenshot analysis for visual understanding of the device 
            🫆 Execution tracing with Arize Phoenix
        
        Requirements:
        - Make it visually appealing and relevant to the topic
        - Include style descriptors (e.g., modern, colorful, professional)
        - Specify image composition and elements
        - Keep it concise but descriptive
        - Make it suitable for social media sharing
        - Don't include quotes around the final output
        
        Make sure to create one of illustration, comic style or drawing. Also mention style and instruction in prompt.
        Return only the image prompt, nothing else.
        """

        response = await self.llm.acomplete(prompt)
        return response.text.strip()

    async def generate_content_from_trend(self, trend_data: dict) -> dict:
        """Generate both Twitter post and image prompt from trend data"""
        trending_topic = trend_data.get("trending_topic", "")
        description = trend_data.get("description", "")
        category = trend_data.get("category", "")

        # Generate Twitter post
        twitter_post = await self.generate_twitter_post(
            trending_topic, description, category
        )

        # Generate image prompt
        image_prompt = await self.generate_image_prompt(trending_topic, twitter_post)

        return {
            "twitter_post": twitter_post,
            "image_prompt": image_prompt,
            "original_trend": trend_data,
        }


async def test_content_generator():
    """Test function for the content generator"""
    generator = ContentGenerator()

    # Test data
    test_trend = {
        "trending_topic": "AI Technology",
        "description": "Latest developments in artificial intelligence",
        "category": "Technology",
    }

    content = await generator.generate_content_from_trend(test_trend)
    print("Generated Content:")
    print(f"Twitter Post: {content['twitter_post']}")
    print(f"Image Prompt: {content['image_prompt']}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_content_generator())
