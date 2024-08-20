from ast import literal_eval
from typing import Any, AsyncGenerator, AsyncIterator, Literal, Mapping

from ollama import AsyncClient, Client, Message, Options

from oterm.config import envConfig

class OllamaLLM:
    def __init__(
        self,
        model="tinyllama:latest",
        system: str | None = None,
        history: list[Message] = [],
        format: Literal["", "json"] = "",
        options: Options = Options(
            top_k=20,
            top_p=0.9,
            min_p=0.0,
            tfs_z=0.5,
            repeat_last_n=33,
            temperature=0.8,
            repeat_penalty=1.2,
            presence_penalty=1.5,
            frequency_penalty=1.0,
            num_thread=4,
            use_mmap=True,
            num_ctx=128,
            num_batch=2,
            mirostat=1,
            mirostat_tau=0.8,
            mirostat_eta=0.6,
            numa=True,
            num_gpu=1,
            main_gpu=1,
            low_vram=False,
            f16_kv=False,
            vocab_only=False,
            use_mlock=False,
        ),
        keep_alive: int = 5,
    ):
        self.model = model
        self.system = system
        self.history = history
        self.format = format
        self.keep_alive = keep_alive
        self.options = options
        self.client = AsyncClient(
            host=envConfig.OLLAMA_URL, verify=envConfig.OTERM_VERIFY_SSL
        )

        if system:
            system_prompt: Message = {"role": "system", "content": system}
            self.history = [system_prompt] + self.history

    async def completion(self, prompt: str, images: list[str] = []) -> str:
        user_prompt: Message = {"role": "user", "content": prompt}
        if images:
            user_prompt["images"] = images
        self.history.append(user_prompt)
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

    async def stream(
        self, prompt: str, images: list[str] = []
    ) -> AsyncGenerator[str, Any]:
        user_prompt: Message = {"role": "user", "content": prompt}
        if images:
            user_prompt["images"] = images
        self.history.append(user_prompt)

        stream: AsyncIterator[dict] = await self.client.chat(
            model=self.model,
            messages=self.history,
            stream=True,
            options=self.options,
            keep_alive=f"{self.keep_alive}m",
            format=self.format,
        )
        text = ""
        async for response in stream:
            ollama_response = response.get("message", {}).get("content", "")
            text += ollama_response
            yield text

        self.history.append({"role": "assistant", "content": text})

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
            if params.get(key):
                if not isinstance(params[key], list):
                    params[key] = [params[key], value]
                else:
                    params[key].append(value)
            else:
                params[key] = value
    return params
