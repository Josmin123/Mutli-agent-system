import asyncio
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console

import os
from dotenv import load_dotenv

async def main() -> None:
    model_client=OpenAIChatCompletionClient(model="gemini-1.5-flash-8b")

    async def get_weather(location:str) -> str:
        return f"The weather in {location} is sunny"  

    assitant=AssistantAgent(
        "Assitant",
        model_client=model_client,
        tools=[get_weather],
    )
    termination=TextMentionTermination("TERMINATE")
    team=RoundRobinGroupChat([assitant],termination_condition=termination)
    await Console(team.run_stream(task="What's the weather in Banglore?"))

asyncio.run(main())    