import asyncio
import os
import json
from typing import List
from dataclasses import dataclass
from dotenv import load_dotenv

from autogen_core import (
    AgentId,
    FunctionCall,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    message_handler,
    CancellationToken
)
from autogen_core.models import (
    ChatCompletionClient,
    LLMMessage,
    SystemMessage,
    UserMessage,
    AssistantMessage,
    FunctionExecutionResult,
    FunctionExecutionResultMessage,
)
from autogen_core.tools import FunctionTool, Tool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

voice_id = "onwK4e9ZLuTAKqWW03F9"


def generate_voiceovers_tool(input: dict) -> dict:
    captions = input.get("captions", [])
    if not isinstance(captions, list):
        raise ValueError("Tool input must contain 'captions' as a list.")

    os.makedirs("voiceovers", exist_ok=True)
    audio_paths = []

    for i, message in enumerate(captions, 1):
        save_file_path = f"voiceovers/voiceover_{i}.mp3"

        if os.path.exists(save_file_path):
            audio_paths.append(save_file_path)
            continue

        response = elevenlabs_client.text_to_speech.convert(
            text=message,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_22050_32",
        )

        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

        audio_paths.append(save_file_path)

    return {"voiceover_paths": audio_paths}


@dataclass
class Message:
    content: str


class ToolUseAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient, tool_schema: List[Tool]) -> None:
        super().__init__("tool_user")
        self._system_messages: List[LLMMessage] = [
            SystemMessage(content="You are a helpful voiceover assistant. Given a list of captions, use the voiceover generation tool to save the files locally. Only respond with TERMINATE once complete.")
        ]
        self._model_client = model_client
        self._tools = tool_schema

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        session: List[LLMMessage] = self._system_messages + [UserMessage(content=message.content, source="user")]

        create_result = await self._model_client.create(
            messages=session,
            tools=self._tools,
            cancellation_token=ctx.cancellation_token,
        )

        if isinstance(create_result.content, str):
            return Message(content=create_result.content)

        session.append(AssistantMessage(content=create_result.content, source="assistant"))

        results = await asyncio.gather(
            *[self._execute_tool_call(call, ctx.cancellation_token) for call in create_result.content]
        )

        session.append(FunctionExecutionResultMessage(content=results))

        create_result = await self._model_client.create(
            messages=session,
            cancellation_token=ctx.cancellation_token,
        )

        return Message(content=create_result.content)

    async def _execute_tool_call(self, call: FunctionCall, cancellation_token: CancellationToken) -> FunctionExecutionResult:
        tool = next((tool for tool in self._tools if tool.name == call.name), None)
        assert tool is not None

        try:
            arguments = json.loads(call.arguments)
            result = await tool.run_json(arguments, cancellation_token)
            return FunctionExecutionResult(
                call_id=call.id, content=tool.return_value_as_string(result), is_error=False, name=tool.name
            )
        except Exception as e:
            return FunctionExecutionResult(call_id=call.id, content=str(e), is_error=True, name=tool.name)


async def main():
    model_client = OpenAIChatCompletionClient(model="gemini-1.5-flash-8b")
    runtime = SingleThreadedAgentRuntime()
    
    voiceover_tool = FunctionTool(generate_voiceovers_tool, description="Generate and save voiceovers for a list of captions")
    tools: List[Tool] = [voiceover_tool]

    await ToolUseAgent.register(runtime, "voiceover_agent", lambda: ToolUseAgent(model_client=model_client, tool_schema=tools))

    runtime.start()
    tool_use_agent = AgentId("voiceover_agent", "default")

    response = await runtime.send_message(
        Message("Generate voiceovers for these captions: ['Hello world', 'This is AI', 'Enjoy the future']"),
        tool_use_agent
    )

    print("\nAgent Response:", response.content)

    await runtime.stop()
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
