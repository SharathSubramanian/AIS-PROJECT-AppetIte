from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ==========================================================
# TRY LOADING YOUR LOCAL LoRA-FINETUNED FLAN-T5-BASE MODEL
# Path given by you: Appetite/src/model/flan_t5_appetite_lora
# This file lives at: src/backend/ml/inference.py
# So the model folder should be at: src/model/flan_t5_appetite_lora
# ==========================================================
try:
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    import torch

    _HAVE_TRANSFORMERS = True
except Exception:
    _HAVE_TRANSFORMERS = False

# Resolve model path relative to repo
MODEL_PATH = (
    Path(__file__).resolve()   # .../src/backend/ml/inference.py
    .parents[2]                # .../src
    / "model"
    / "flan_t5_appetite_lora"
)

tokenizer = None
model = None
device = "cpu"
USE_MODEL = False

if _HAVE_TRANSFORMERS:
    try:
        if MODEL_PATH.exists():
            tokenizer = T5Tokenizer.from_pretrained(str(MODEL_PATH))
            model = T5ForConditionalGeneration.from_pretrained(str(MODEL_PATH))
            logger.info("Loaded local LoRA fine-tuned FLAN-T5 model from %s", MODEL_PATH)
        else:
            # If the local folder is missing, fallback to hub base model
            tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
            model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
            logger.warning(
                "Local model folder not found at %s. Falling back to google/flan-t5-base.",
                MODEL_PATH,
            )

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        model.eval()
        USE_MODEL = True
    except Exception as e:
        # Last-resort attempt with Auto* (handles odd configs)
        try:
            tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
            model = AutoModelForSeq2SeqLM.from_pretrained(str(MODEL_PATH))
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model.to(device)
            model.eval()
            USE_MODEL = True
            logger.info("Loaded local model with Auto* classes from %s", MODEL_PATH)
        except Exception as e2:
            logger.warning("Model load failed, using fallback. Error: %s / %s", e, e2)
            USE_MODEL = False


# ==========================================================
# PROMPT
# ==========================================================
_PROMPT_TEMPLATE = """You are a helpful chef assistant.

Given these ingredients:
{ingredients}

Category preference: {category}
Mode: {mode}

Generate a single recipe as ONLY valid JSON with keys:
"title": string,
"ingredients": list of strings,
"instructions": string

Rules:
- Title must be under 8 words.
- Instructions must be a normal paragraph, no bullet points.
- DO NOT include ingredients inside the title.
- DO NOT repeat sentences.
- DO NOT add extra fields.
"""


def _build_prompt(ingredients: List[str], category: Optional[str], mode: str) -> str:
    ing_text = ", ".join(ingredients)
    cat_text = category if category else "any"
    return _PROMPT_TEMPLATE.format(
        ingredients=ing_text,
        category=cat_text,
        mode=mode,
    )


# ==========================================================
# GENERATION
# ==========================================================
def _generate_with_model(prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            top_p=0.9,
            temperature=0.8,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def _parse_json(text: str) -> Optional[Dict]:
    # Try direct JSON first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to locate a JSON object inside text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return None
    return None


# ==========================================================
# FALLBACK RECIPE (if model not available)
# ==========================================================
def _fallback_recipe(
    ingredients: List[str],
    category: Optional[str] = None,
    mode: str = "inventory",
) -> Dict:
    ing = [i.strip().lower() for i in ingredients if i and i.strip()]

    title_patterns = [
        "Savory {main} Delight",
        "Quick {main} Skillet",
        "Healthy {main} Bowl",
        "Golden {main} Skillet",
        "Comfort {main} Mix",
    ]

    main = ", ".join(ing[:2]).title() if ing else "Pantry"
    title = random.choice(title_patterns).format(main=main)

    instructions = (
        f"Begin by preparing {', '.join(ing) if ing else 'your ingredients'}. "
        "Heat a pan over medium heat and add oil. "
        "Add the ingredients and sauté until fragrant. "
        "Season well and continue cooking until tender. "
        "Serve warm."
    )

    return {
        "title": title,
        "ingredients": ing + ["salt", "pepper", "oil"],
        "instructions": instructions,
    }


# ==========================================================
# PUBLIC ENTRYPOINT
# ==========================================================
def generate_recipe(
    ingredients: List[str],
    category: Optional[str] = None,
    mode: str = "inventory",
) -> Dict:
    ingredients = [i.strip() for i in ingredients if i and i.strip()]

    if USE_MODEL:
        try:
            prompt = _build_prompt(ingredients, category, mode)
            raw = _generate_with_model(prompt)
            parsed = _parse_json(raw)

            if parsed:
                return parsed

            logger.warning("Model returned non-JSON, fallback.")
        except Exception as e:
            logger.warning("Model generation failed: %s", e)

    return _fallback_recipe(ingredients, category, mode)