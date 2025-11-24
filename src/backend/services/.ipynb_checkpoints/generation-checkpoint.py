# src/backend/services/generation.py
from typing import Optional, List, Union, Dict, Any
import json
import re
import torch

from ..config import MAX_INPUT_LEN, MAX_OUTPUT_LEN, TEMPERATURE, TOP_P, TOP_K, NUM_BEAMS
from ..deps import get_model_and_tokenizer, get_device


def _normalize_ingredients(ingredients: Union[str, List[str]]) -> str:
    if isinstance(ingredients, list):
        return ", ".join([i.strip() for i in ingredients if i.strip()])
    return str(ingredients).strip()


def _postprocess_to_json(text: str, ingredients_list: List[str], category: Optional[str]) -> Dict[str, Any]:
    title = "Generated Recipe"
    instructions = text.strip()

    m = re.search(r"Title:\s*(.+)", text)
    if m:
        title = m.group(1).strip()

    if "Instructions:" in text:
        instructions = text.split("Instructions:", 1)[1].strip()

    return {
        "title": title,
        "ingredients": ingredients_list,
        "instructions": instructions,
        "category": category,
    }


def generate_recipe_text(
    ingredients_text: str,
    category: Optional[str] = None,
    max_new_tokens: int = MAX_OUTPUT_LEN,
) -> str:
    model, tokenizer = get_model_and_tokenizer()
    device = get_device()

    cat_part = f"{category} " if category else ""

    prompt = (
        f"Given the following ingredients: {ingredients_text}\n"
        f"Write a {cat_part}cooking recipe.\n"
        f"Format STRICTLY as:\n"
        f"Title: <recipe title>\n\n"
        f"Instructions:\n"
        f"1. <step 1>\n"
        f"2. <step 2>\n"
        f"3. <step 3>\n"
        f"Each step MUST be on a new line.\n"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_LEN,
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            num_beams=NUM_BEAMS,
            no_repeat_ngram_size=3,
            early_stopping=True,
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Instructions:" in text:
        text = text.replace("Instructions:", "\n\nInstructions:\n")
    text = text.replace(". ", ".\n")
    return text


def generate_with_model(
    ingredients: Union[str, List[str]],
    category: Optional[str] = None,
    mode: str = "quick",
) -> str:
    ingredients_text = _normalize_ingredients(ingredients)
    ingredients_list = ingredients if isinstance(ingredients, list) else [
        i.strip() for i in ingredients_text.split(",") if i.strip()
    ]

    raw_text = generate_recipe_text(
        ingredients_text=ingredients_text,
        category=category,
        max_new_tokens=MAX_OUTPUT_LEN,
    )

    payload = _postprocess_to_json(raw_text, ingredients_list, category)
    return json.dumps(payload)