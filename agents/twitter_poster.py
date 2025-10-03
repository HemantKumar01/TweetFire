#!/usr/bin/env python3
import asyncio
import json
from droidrun import AdbTools, DroidAgent
from llama_index.llms.google_genai import GoogleGenAI
from agents.prompts.prompts import OPEN_TWITTER_CREATE_POST_GOAL
from dotenv import load_dotenv
import os

load_dotenv()


async def post_to_twitter(post_content: str, has_image: bool = True):
    """Post content to Twitter/X with optional image"""
    # Load adb tools for the first connected device
    tools = AdbTools()

    # Set up the Gemini LLM
    llm = GoogleGenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini-2.5-flash",
    )

    # Create the DroidAgent
    agent = DroidAgent(
        goal=OPEN_TWITTER_CREATE_POST_GOAL(post_content, has_image),
        llm=llm,
        tools=tools,
        enable_tracing=True,
        save_trajectories="action",
        reasoning=True,
        vision=True,
    )

    # Run the agent
    result = await agent.run()
    print(f"Twitter poster - Success: {result['success']}")

    if result.get("output"):
        try:
            # Parse the JSON output
            post_result = json.loads(result["output"])
            print(f"Twitter post status: {post_result.get('message', 'Unknown')}")
            return post_result
        except json.JSONDecodeError:
            print(f"Could not parse Twitter post result: {result['output']}")
            return {"success": False, "message": "Failed to parse Twitter post result"}
    else:
        print("No Twitter post result")
        return {"success": False, "message": "No result from Twitter posting"}


if __name__ == "__main__":
    # Test with sample content
    test_content = "Excited about the latest tech trends! 🚀 #TechNews #Innovation"
    asyncio.run(post_to_twitter(test_content, has_image=False))
