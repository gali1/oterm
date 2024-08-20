import asyncio
import json
from enum import Enum
from pathlib import Path
from typing import Literal, Optional
from oterm.ollamaclient import OllamaLLM, Options

class Author(Enum):
    USER = "me"
    OLLAMA = "ollama"

class ChatContainer:
    def __init__(
        self,
        db_id: int,
        chat_name: str,
        model: str = "llama3.1",
        context: Optional[list[int]] = None,
        messages: Optional[list[tuple[Author, str]]] = None,
        system: Optional[str] = None,
        format: Literal["", "json"] = "",
        parameters: Optional[Options] = None,
        keep_alive: int = 5,
    ) -> None:
        if context is None:
            context = []
        if messages is None:
            messages = []
        if parameters is None:
            parameters = {}

        self.ollama = OllamaLLM(
            model=model,
            context=context,
            system=system,
            format=format,
            options=parameters,
            keep_alive=keep_alive,
        )
        self.chat_name = chat_name
        self.db_id = db_id
        self.messages = messages
        self.system = system
        self.format = format
        self.parameters = parameters
        self.keep_alive = keep_alive
        self.images = []

    async def send_message(self, message: str) -> str:
        self.messages.append((Author.USER, message))
        response = ""
        async for text in self.ollama.stream(message, [img for _, img in self.images]):
            response = text
        self.messages.append((Author.OLLAMA, response))
        return response

    async def process_input(self, input_text: str) -> None:
        if input_text.strip() == 'exit':
            return
        response = await self.send_message(input_text)
        print(f"Ollama: {response}")

async def main():
    # Initialize the ChatContainer
    chat_container = ChatContainer(
        db_id=1,
        chat_name="Test Chat",
        model="llama3.1",
        context=[],
        messages=[],
        system=None,
        format="",
        parameters={},
        keep_alive=5
    )
    
    print("Welcome to the Chat CLI. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.strip() == 'exit':
            break
        await chat_container.process_input(user_input)

# Run the CLI interface
if __name__ == "__main__":
    asyncio.run(main())
