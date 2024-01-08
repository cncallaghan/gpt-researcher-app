import os
import threading
import logging
import json

from colorama import Fore, Style
from gpt_researcher.master.prompts import auto_agent_instructions

from fastapi import WebSocket
from typing import Optional
from openai import AzureOpenAI


class AzureOpenAISingleton:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        """Static access method."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = AzureOpenAI(
                        api_version=os.environ["AZURE_OPENAI_VERSION"],
                        api_key=os.environ["OPENAI_API_KEY"],
                        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                    )
                    print(cls._instance.base_url)
        return cls._instance


async def create_azure_chat_completion(
    messages: list,  # type: ignore
    model: Optional[str] = None,
    temperature: float = 1.0,
    max_tokens: Optional[int] = None,
    llm_provider: Optional[str] = None,
    stream: Optional[bool] = False,
    websocket: WebSocket | None = None,
) -> str:
    # validate input
    if model is None:
        raise ValueError("Model cannot be None")
    if max_tokens is not None and max_tokens > 8001:
        raise ValueError(f"Max tokens cannot be more than 8001, but got {max_tokens}")

    # create response
    for attempt in range(1):  # maximum of 10 attempts
        response = await send_chat_completion_request(
            messages, model, temperature, max_tokens, stream, llm_provider, websocket
        )
        return response

    logging.error("Failed to get response from OpenAI API")
    raise RuntimeError("Failed to get response from OpenAI API")


async def send_chat_completion_request(
    messages, model, temperature, max_tokens, stream, llm_provider, websocket
):
    if not stream:
        result = AzureOpenAISingleton.get_instance().chat.completions.create(
            model="aoai-deploy-1",  # Change model here to use different models
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            # provider=llm_provider,  # Change provider here to use a different API
        )
        logging.info(result)
        logging.info(type(result))
        logging.info(dir(result))
        return result.choices[0].message.content
    else:
        return await stream_response(
            model, messages, temperature, max_tokens, llm_provider, websocket
        )


async def stream_response(
    model, messages, temperature, max_tokens, llm_provider, websocket=None
):
    paragraph = ""
    response = ""

    for chunk in AzureOpenAISingleton.get_instance().chat.completions.create(
        model="aoai-deploy-1",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        provider=llm_provider,
        stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            response += content
            paragraph += content
            if "\n" in paragraph:
                if websocket is not None:
                    await websocket.send_json({"type": "report", "output": paragraph})
                else:
                    print(f"{Fore.GREEN}{paragraph}{Style.RESET_ALL}")
                paragraph = ""
    return response


def choose_agent(smart_llm_model: str, llm_provider: str, task: str) -> dict:
    try:
        response = create_azure_chat_completion(
            model=smart_llm_model,
            messages=[
                {"role": "system", "content": f"{auto_agent_instructions()}"},
                {"role": "user", "content": f"task: {task}"},
            ],
            temperature=0,
            llm_provider=llm_provider,
        )
        agent_dict = json.loads(response)
        print(f"Agent: {agent_dict.get('server')}")
        return agent_dict
    except Exception as e:
        print(f"{Fore.RED}Error in choose_agent: {e}{Style.RESET_ALL}")
        return {
            "server": "Default Agent",
            "agent_role_prompt": "You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text.",
        }
