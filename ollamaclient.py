import asyncio
from ast import literal_eval
from typing import Any, AsyncGenerator, AsyncIterator, Literal, Mapping, Optional

from ollama import AsyncClient, Client, Message, Options

from oterm.config import envConfig

class OllamaLLM:
    def __init__(
        self,
        model="tinyllama:latest",
        system: Optional[str] = None,
        history: Optional[list[Message]] = None,
        format: Literal["", "json"] = "",
        options: Options = Options(
            top_k=20,              # Maintain balance between quality and performance
            top_p=0.8,             # Slightly reduced for efficiency
            min_p=0.0,             # Ensure diversity
            tfs_z=0.5,             # Balanced frequency sampling
            repeat_last_n=33,      # Manage repetition without excessive overhead
            temperature=0.7,       # Slightly lower for more focused responses
            repeat_penalty=1.1,    # Balanced penalty for repetition
            presence_penalty=1.0,  # Balanced penalty for novelty
            frequency_penalty=1.0,  # Balanced frequency penalty
            num_thread=4,          # Adjust based on system capabilities
            use_mmap=True,         # Efficient memory usage
            num_ctx=128,           # Reduce context size for performance
            num_batch=2,           # Increase batch size for throughput
            mirostat=1,            # Default dynamic sampling
            mirostat_tau=0.7,      # Balanced parameter for mirostat
            mirostat_eta=0.5,      # Balanced parameter for mirostat
            numa=True,             # Use NUMA if supported
            num_gpu=1,             # Use one GPU unless more are available
            main_gpu=1,            # Main GPU index
            low_vram=False,        # Use standard VRAM mode
            f16_kv=False,          # Use standard precision for key/value matrices
            vocab_only=False,      # Load full model
            use_mlock=False,       # Standard memory locking
        ),
        keep_alive: int = 5,
    ):
        self.model = model
        self.system = system
        self.history = history if history is not None else []
        self.format = format
        self.keep_alive = keep_alive
        self.options = options
        self.client = AsyncClient(
            host=envConfig.OLLAMA_URL, verify=envConfig.OTERM_VERIFY_SSL
        )

        if system:
            system_prompt: Message = {"role": "system", "content": system}
            self.history = [system_prompt] + self.history

    async def completion(self, prompt: str, images: Optional[list[str]] = None) -> str:
        user_prompt: Message = {"role": "user", "content": prompt}
        if images:
            user_prompt["images"] = images
        self.history.append(user_prompt)
        
        try:
            response = await self.client.chat(
                model=self.model,
                messages=self.history,
                keep_alive=f"{self.keep_alive}m",
                options=self.options,
                format=self.format,
            )
            ollama_response = response.get("message", {}).get("content", "")
            self.history.append({"role": "assistant", "content": ollama_response})
            return ollama_response
        except Exception as e:
            print(f"Error during completion: {e}")
            return ""

    async def stream(
        self, prompt: str, images: Optional[list[str]] = None
    ) -> AsyncGenerator[str, Any]:
        user_prompt: Message = {"role": "user", "content": prompt}
        if images:
            user_prompt["images"] = images
        self.history.append(user_prompt)

        try:
            stream: AsyncIterator[dict] = await self.client.chat(
                model=self.model,
                messages=self.history,
                stream=True,
                options=self.options,
                keep_alive=f"{self.keep_alive}m",
                format=self.format,
            )
            buffer = ""
            async for response in stream:
                ollama_response = response.get("message", {}).get("content", "")
                if ollama_response:
                    buffer += ollama_response
                    yield buffer
                    # Optionally, you could use asyncio.sleep(0) to yield control back to the event loop
                    # for higher responsiveness if needed.
                    # await asyncio.sleep(0)
            self.history.append({"role": "assistant", "content": buffer})
        except Exception as e:
            print(f"Error during streaming: {e}")

    @staticmethod
    def list() -> Mapping[str, Any]:
        client = Client(host=envConfig.OLLAMA_URL, verify=envConfig.OTERM_VERIFY_SSL)
        return client.list()

    @staticmethod
    def show(model: str) -> Mapping[str, Any]:
        client = Client(host=envConfig.OLLAMA_URL, verify=envConfig.OTERM_VERIFY_SSL)
        return client.show(model)

def parse_ollama_parameters(parameter_text: str) -> Options:
    lines = parameter_text.split("\n")
    params = Options()
    for line in lines:
        if line.strip():
            key, value = line.split(maxsplit=1)
            try:
                value = literal_eval(value)
            except (SyntaxError, ValueError):
                pass
            if hasattr(params, key):
                current_value = getattr(params, key)
                if not isinstance(current_value, list):
                    setattr(params, key, [current_value, value])
                else:
                    current_value.append(value)
            else:
                setattr(params, key, value)
    return params