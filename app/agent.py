from agents import Agent

from app.tools.files import read_file, scan_directory, write_file
from app.tools.memory import recall_memory, save_memory

import io
import os
import sys

primary_path = os.path.dirname(os.path.abspath(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", write_through=True)
file_path = os.path.join(primary_path, "base", "personal.txt")


def create_yuri_agent(model) -> Agent:
    with open(file_path, "r", encoding="utf-8") as file:
        base_personal_knowledge = file.read()
    return Agent(
        name="Yuri",
        tools=[
            save_memory,
            recall_memory,
            scan_directory,
            read_file,
            write_file,
        ],
        instructions=(base_personal_knowledge),
        model=model,
    )
