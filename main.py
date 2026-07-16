import os
from agents import Agent, Runner
from agents import set_default_openai_api, set_default_openai_client, set_tracing_export_api_key, set_tracing_disabled
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

set_default_openai_api("chat_completions")
set_tracing_disabled(True)

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

model = OpenAIChatCompletionsModel(
    model="llama3.2:3b-instruct-fp16",
    openai_client=client,
)

agent = Agent(name="Assistant",
              instructions="You are a helpful assistant", model=model)

result = Runner.run_sync(
    agent, "Write a haiku about recursion in programming.")
print(result.final_output)
