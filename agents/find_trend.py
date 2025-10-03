#!/usr/bin/env python3
import asyncio
import json
import re
from droidrun import AdbTools, DroidAgent
from llama_index.llms.google_genai import GoogleGenAI
from agents.prompts.prompts import OPEN_CHROME_GOOGLE_TRENDS_GOAL
from dotenv import load_dotenv
import os

load_dotenv()


async def find_trend():
    """Find trending topics using Chrome and Google Trends"""
    # Load adb tools for the first connected device
    tools = AdbTools()

    # Set up the Gemini LLM
    llm = GoogleGenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini-2.5-pro",
    )

    # Create the DroidAgent
    agent = DroidAgent(
        goal=OPEN_CHROME_GOOGLE_TRENDS_GOAL(),
        llm=llm,
        tools=tools,
        enable_tracing=True,
        save_trajectories="action",
        reasoning=True,
        vision=True,
    )
    # Run the agent
    result = await agent.run()
    print(f"Trend finder - Success: {result['success']}")

    if result.get("output"):
        try:
            # Parse the JSON output
            trend_data = json.loads(result["output"])
            print(
                f"Found trending topic: {trend_data.get('trending_topic', 'Unknown')}"
            )
            return trend_data
        except json.JSONDecodeError:
            print(f"Could not parse trend data: {result['output']}")
            # Return a fallback trend
            return {
                "trending_topic": "Latest Technology Trends",
                "description": "Current technology trends and innovations",
                "category": "Technology",
            }
    else:
        print("No trend data found, using fallback")
        return {
            "trending_topic": "Daily Tech News",
            "description": "Latest technology news and updates",
            "category": "Technology",
        }


if __name__ == "__main__":
    asyncio.run(find_trend())
