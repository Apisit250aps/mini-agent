import asyncio
import time

import typer
from agents import Agent, Runner
from agents.items import TResponseInputItem
from agents import set_default_openai_api, set_tracing_disabled
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

from app.agent import create_yuri_agent
from app.logging.chat_logger import ChatLogger
from config import settings

set_default_openai_api("chat_completions")
set_tracing_disabled(True)

client = AsyncOpenAI(
    base_url=settings.OLLAMA_BASE_URL,
    api_key=settings.OLLAMA_API_KEY,
)

model = OpenAIChatCompletionsModel(
    model=settings.OLLAMA_MODEL,
    openai_client=client,
)

agent: Agent = create_yuri_agent(model)

app = typer.Typer(add_completion=False, help="CLI แชตกับยูริ")
console = Console()


async def chat_loop() -> None:
    logger = ChatLogger()

    welcome = Text(f"เริ่มแชตกับยูริได้เลย (พิมพ์ exit, quit หรือ ออก เพื่อจบโปรแกรม)")
    console.print(Panel(welcome, title=f"Yuri CLI  •  session {logger.session_id}", border_style="cyan"))

    input_items: list[TResponseInputItem] = []

    while True:
        try:
            user_text = console.input("[bold green]master:[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold magenta]Yuri:[/bold magenta] ไว้คุยกันใหม่นะคะ!")
            break

        if not user_text:
            continue

        if user_text.lower() in {"exit", "quit"} or user_text == "ออก":
            console.print("[bold magenta]Yuri:[/bold magenta] บ๊ายบายค่ะ แล้วเจอกันใหม่!")
            break

        input_items.append({"role": "user", "content": user_text})

        t0 = time.perf_counter()
        result = await Runner.run(agent, input_items)
        duration_ms = int((time.perf_counter() - t0) * 1000)

        reply = (result.final_output or "").strip()
        console.print(f"[bold magenta]Yuri:[/bold magenta] {reply}")

        logger.log_turn(
            user_content=user_text,
            result=result,
            duration_ms=duration_ms,
            model_name=settings.OLLAMA_MODEL,
            output_content=reply,
        )

        input_items = result.to_input_list()


@app.command()
def chat() -> None:
    """เริ่มโหมดสนทนากับยูริ"""
    asyncio.run(chat_loop())


def main() -> None:
    app()


if __name__ == "__main__":
    main()

