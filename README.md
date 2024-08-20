
---

# Oterm - Text-Based Terminal Client for Ollama [Optimized!]

Oterm is a text-based terminal client designed for interacting with [Ollama](https://github.com/jmorganca/ollama) servers.

## Features

- Intuitive and simple terminal UI.
- Optimized for use on a variety of devices.
- Efficient data handling with SQLite for storing chat sessions.
- Customizable model system prompts and parameters.
- Supports any models available in Ollama or your own custom models.

## Installation and Usage

To simplify installation and configuration, use the provided `auto-start.sh` script:

```bash
./auto-start.sh
```

This script automatically:

- Determines the Python version installed on your system.
- Installs necessary dependencies using `pip`.
- Copies the `oterm` executable to `/usr/local/bin/`.
- Copies the `oterm` package to the appropriate Python site-packages directory.
- Configures Oterm to work with your Ollama server.

### Environment Variables

Oterm requires the following environment variables for configuration:

- **OLLAMA_URL**: URL of the Ollama API (e.g., `http://0.0.0.0:11434`).
- **OTERM_VERIFY_SSL**: Set to `False` to disable SSL verification.

### Code Reference

The following Python code snippet demonstrates integration with Ollama using `OllamaLLM` class and `parse_ollama_parameters` function:

```python
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
            numa=False,
            num_gpu=0,
            main_gpu=0,
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
```

### Further Customization

For advanced customization of Ollama parameters and integration, refer to the `OllamaLLM` class and `parse_ollama_parameters` function. These provide flexibility in setting up and interacting with different Ollama models directly from your terminal.

### Screenshots

![Chat](screenshots/chat.png)
![Model Selection](screenshots/model_selection.png)
![Image Selection](screenshots/image_selection.png)

## License

This project is licensed under the [MIT License](LICENSE).

---
