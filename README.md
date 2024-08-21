
# **oterm-quick client [oterm-quick]**

## **Project Overview**

The oterm-quick client is a Python-based interface designed to interact with language models using Ollama's services. This project allows developers to easily configure and communicate with a variety of language models, providing flexibility through custom options and configurations. The focus of this project is on providing a seamless integration, robust configuration management, and ease of use for both simple and advanced use cases.

## **Table of Contents**

- [Project Overview](#project-overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Quick Start [LIKE REAL QUICK!]](#quick-start-like-real-quick)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Docker Installation](#docker-installation)
- [Running the Tests](#running-the-tests)
  - [Breakdown of End-to-End Tests](#breakdown-of-end-to-end-tests)
  - [Coding Style Tests](#coding-style-tests)
- [Usage](#usage)
  - [Basic Example](#basic-example)
  - [Streaming Responses](#streaming-responses)
  - [Listing Available Models](#listing-available-models)
- [Deployment](#deployment)
- [Configuration Details](#configuration-details)
  - [EnvConfig](#envconfig)
  - [AppConfig](#appconfig)
- [Code Explanation](#code-explanation)
  - [OllamaLLM Class](#ollamallm-class)
  - [Optimizations](#optimizations)
- [Built With](#built-with)
- [Versioning](#versioning)
- [Screenshots](#screenshots)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## **Features**

- **Async and Sync API:** Supports both asynchronous and synchronous API calls for flexibility.
- **Custom Configurations:** Easily configure model options and environment settings.
- **Streaming Support:** Stream responses from models for real-time interaction.
- **Configuration Management:** Centralized configuration through environment variables and JSON files.

## **Getting Started**

These instructions will help you get a copy of the project up and running on your local machine for development and testing purposes. See the [Deployment](#deployment) section for notes on how to deploy the project on a live system.

### **Quick Start [LIKE REAL QUICK!]**

To simplify installation and configuration, use the provided `auto-start.sh` script:

```bash
./auto-start.sh
```

### **Prerequisites**

Before you can run the oterm-quick client, ensure you have the following installed:

- **Python 3.8+**: The core programming language required for this project.
- **pip**: Python package manager to install dependencies.
- **Git**: For cloning the repository.

You can install Python and pip from the official Python website:

```bash
# On Ubuntu/Debian-based systems
sudo apt-get update
sudo apt-get install python3 python3-pip

# On macOS using Homebrew
brew install python
```

### **Installation**

Follow these steps to set up your development environment:

1. **Clone the Repository**: Start by cloning the project repository to your local machine.

   ```bash
   git clone https://github.com/keli2/ollama-llm-client.git
   cd ollama-llm-client
   ```

2. **Install Dependencies**: Use `pip` to install the necessary Python packages.

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**: The project uses environment variables for configuration. Create a `.env` file in the root directory with the following content:

   ```env
   OLLAMA_HOST=0.0.0.0:11434
   OLLAMA_URL=http://0.0.0.0:11434
   OTERM_VERIFY_SSL=True
   ```

4. **Verify Installation**: Run a simple command to verify that the setup was successful.

   ```bash
   python -c "from ollamaclient import OllamaLLM; print(OllamaLLM.list())"
   ```

   This command should list available models if everything is set up correctly.

### **Docker Installation**

For a quick and isolated environment setup, you can use Docker. Follow these steps to build and run the Docker image:

1. **Build the Docker Image**: Navigate to the directory containing your Dockerfile and build the image.

   ```bash
   docker build -t oterm-quick .
   ```

2. **Run the Docker Container**: Start the container from the built image.

   ```bash
   docker run -it --rm oterm-quick
   ```

   This will execute the `oterm` command as defined in the Dockerfile.

Here’s a brief explanation of the Dockerfile used:

- **Base Image**: Uses `python:3.10-slim` as the base image with Python pre-installed.
- **Environment Setup**: Sets up the environment for non-interactive package installation.
- **Dependencies**: Installs required packages and copies project files into the image.
- **Package Installation**: Installs the `uv` package and other dependencies from `requirements.txt`.
- **Executable Setup**: Copies the executable file to the appropriate directory and sets the necessary permissions.
- **Entrypoint**: Specifies the default command to run when the container starts.

## **Running the Tests**

The project includes a suite of automated tests to ensure code quality and functionality. Here's how you can run them:

### **Breakdown of End-to-End Tests**

End-to-end tests verify the complete flow of the application, from initialization to generating model responses. These tests ensure that the interaction with Ollama models works as expected.

```python
def test_completion():
    client = OllamaLLM(model="test_model")
    response = client.completion("Test prompt")
    assert response.startswith("Test"), "Unexpected response from the model"
```

### **Coding Style Tests**

Coding style tests (e.g., PEP 8 compliance) ensure that the code adheres to Python's style guidelines. You can use tools like `flake8` or `pylint` to check the coding style.

```bash
# Run flake8 to check for coding style issues
flake8 ollamaclient.py
```

## **Usage**

### **Basic Example**

Here’s a simple example of how to use the OllamaLLM class to generate a response from a model:

```python
from ollamaclient import OllamaLLM

async def main():
    client = OllamaLLM(model="your_model")
    response = await client.completion("Hello, how are you?")
    print(response)

# Run the main function
import asyncio
asyncio.run(main())
```

### **Streaming Responses**

You can also stream responses in real-time:

```python
async def main():
    client = OllamaLLM(model="your_model")
    async for text in client.stream("Tell me a story about a hero"):
        print(text)

# Run the main function
import asyncio
asyncio.run(main())
```

### **Listing Available Models**

To list all available models:

```python
from ollamaclient import OllamaLLM

models = OllamaLLM.list()
print(models)
```

## **Deployment**

To deploy this project on a live system, follow these steps:

1. **Prepare the Environment**: Ensure the live system has all prerequisites installed, as mentioned in the [Getting Started](#getting-started) section.
2. **Environment Variables**: Set up environment variables specific to the production environment, such as the production host URL.
3. **Run the Application**: Start the application, ensuring it connects to the correct instance of Ollama.

```bash
python run_app.py
```

4. **Monitor Logs**: Regularly check logs for any issues and ensure the application is running smoothly.

## **Configuration Details**

### **EnvConfig**

The `EnvConfig` class in `config.py` is responsible for mapping environment variables to class attributes. This allows for easy configuration and overriding of defaults. Here’s a snippet showing how environment variables are parsed:

```python
class EnvConfig:
    ENV: str = "development"

    def __init__(self, env: dict[str, str]):
        for field, var_type in get_type_hints(EnvConfig).items():
            if field.isupper():
                self._set_field(env, field, var_type)
```

### **AppConfig**

The `AppConfig` class manages application-specific configurations. It reads and writes to a JSON file, ensuring persistence across sessions.

```python
class AppConfig:
    def set(self, key: str, value: Any):
        """Set a configuration value and save it."""
        self._data[key] = value
        self.save()
```

## **Code Explanation**

### **OllamaLLM Class**

The `OllamaLLM` class in `ollamaclient.py` serves as the main interface to the Ollama models. It allows both synchronous and asynchronous interaction with models, supports real-time streaming, and includes extensive options for customization.

Here is the implementation of the `OllamaLLM` class:

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
        format:

 Literal["", "json"] = "",
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
```

### **Optimizations**

- **Asynchronous Support:** The `AsyncClient` allows for non-blocking calls, which is essential for handling large volumes of requests or long-running tasks.
- **Stream Responses:** By streaming responses, the system can start processing output before the entire response is generated, enhancing real-time use cases.
- **Extensive Customization:** The `Options` class provides fine-grained control over the model's behavior, including sampling methods, penalties, and hardware settings.

**Future Improvements:**

- **Error Handling:** The current code is functional, adding more robust error handling, particularly around network failures and unexpected API responses, could make the library more resilient.
- **Caching:** Implementing a caching mechanism for frequent requests could reduce latency and improve performance.
- **Enhanced Testing:** There are tests in place, expanding the test suite to cover more edge cases and integrating it with CI/CD pipelines would be beneficial.

## **Built With**

- [Python](https://www.python.org/) - The programming language used.
- [ollama](https://ollama.com/) - The underlying API for interacting with the models.
- [asyncio](https://docs.python.org/3/library/asyncio.html) - Used for asynchronous programming in Python.

## **Versioning**

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/keli2/ollama-llm-client/tags).

### Screenshots

![Chat](screenshots/chat.png)
![Model Selection](screenshots/model_selection.png)
![Image Selection](screenshots/image_selection.png)

## **License**

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## **Acknowledgments**

- Special thanks to the developers and contributors of the libraries and tools used in this project.
- Any other individuals or resources that contributed to the success of this project.
