#!/usr/bin/env python3
import asyncio
import json
from droidrun import AdbTools, DroidAgent
from llama_index.llms.google_genai import GoogleGenAI
from agents.prompts.prompts import OPEN_GEMINI_CREATE_IMAGE_GOAL
from dotenv import load_dotenv
import os

load_dotenv()


async def generate_image(image_prompt: str):
    """Generate image using Gemini with the provided prompt"""
    # Load adb tools for the first connected device
    tools = AdbTools()
    # Set up the Gemini LLM
    llm = GoogleGenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini-2.5-flash",
    )

    # Create the DroidAgent
    agent = DroidAgent(
        goal=OPEN_GEMINI_CREATE_IMAGE_GOAL(image_prompt),
        llm=llm,
        tools=tools,
        enable_tracing=True,
        save_trajectories="action",
        reasoning=True,
        vision=True,
    )

    # Run the agent
    result = await agent.run()
    print(f"Image generator - Success: {result['success']}")

    if result.get("output"):
        try:
            # Parse the JSON output
            image_result = json.loads(result["output"])
            print(f"Image generation status: {image_result.get('message', 'Unknown')}")
            return image_result
        except json.JSONDecodeError:
            print(f"Could not parse image generation result: {result['output']}")
            return {
                "success": False,
                "message": "Failed to parse image generation result",
            }
    else:
        print("No image generation result")
        return {"success": False, "message": "No result from image generation"}


if __name__ == "__main__":
    # Test with a sample prompt
    test_prompt = (
        "A futuristic cityscape with flying cars and neon lights, digital art style"
    )
    asyncio.run(generate_image(test_prompt))
