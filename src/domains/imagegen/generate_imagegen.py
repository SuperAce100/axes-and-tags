import base64
import re
import os
import json
import numpy as np
from pydantic import BaseModel
import requests
from designspace import Generation, DesignSpace
from models.llms import llm_call, text_model
import fal_client
from rich.progress import track
from domains.imagegen.prompts import *
from typing import List, Tuple, Dict
from rich.console import Console

img_model = "fal-ai/flux/schnell"

def expand_prompt(concept: str, design_space: DesignSpace, model: str = text_model, examples: str = "") -> str:
    return llm_call(image_gen_expand_user_prompt.format(concept=concept, design_space=design_space, examples=examples), system_prompt=image_gen_expand_system_prompt, temperature=1, model=model)

def generate_image(concept: str, design_space: DesignSpace, image_model: str = img_model, text_model: str = text_model) -> Generation:
    prompt = expand_prompt(concept, design_space, text_model)

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    result = fal_client.subscribe(
        image_model,
        arguments={
            "prompt": prompt,
            "image_size": {
                "width": 512,
                "height": 512
            }
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    image_url = result['images'][0]['url']
    print(image_url)

    response = requests.get(image_url)
    image_data = response.content
    image_base64 = base64.b64encode(image_data).decode('utf-8').replace('"', '\\"')

    return Generation(prompt=prompt, content=image_base64)



