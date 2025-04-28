from openai import OpenAI
from pydantic import BaseModel
import tiktoken
from typing import List
import os
import dotenv

dotenv.load_dotenv()

text_model = "openai/gpt-4.1-mini"
# text_model = "anthropic/claude-3.7-sonnet"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

cerebras_client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)
    
cerebras_model = "llama-3.3-70b"


def llm_call(
    prompt: str,
    system_prompt: str = None,
    model: str = text_model,
    **kwargs
):
    """
    Make a LLM call

    ### Args:
        `prompt` (`str`): The user prompt to send to the LLM.
        `system_prompt` (`str`, optional): System-level instructions for the LLM. Defaults to None.
        `model` (`str`, optional): Model identifier to use. Defaults to "gpt-4o-mini".

    ### Returns:
        The LLM's response, either as raw text or as a parsed object according to `response_format`.
    """
    messages = [
        {"role": "system", "content": system_prompt} if system_prompt else None,
        {"role": "user", "content": prompt},
    ]
    messages = [msg for msg in messages if msg is not None]

    print(messages)

    new_kwargs = {**kwargs, "model": model, "messages": messages}

    if "cerebras" in model:
        cur_client = cerebras_client
        new_kwargs["model"] = cerebras_model
    else:
        cur_client = client

    return cur_client.chat.completions.create(**new_kwargs).choices[0].message.content



if __name__ == "__main__":
    print(llm_call("What is the capital of the moon?"))
    # prompt = "What is the capital of the moon?"
    # response = llm_call(prompt)
    # print(response)

    # messages = [
    #     {"role": "user", "content": prompt}
    # ]
    # response = llm_call_messages(messages)
    # print(response)
