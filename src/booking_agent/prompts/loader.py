from pathlib import Path
from typing import Optional

PROMPT_DIR = Path(__file__).parent

def load_prompt(name: str, persona: Optional[str] = None) -> str:
    """
    Load a text prompt and return a LangChain PromptTemplate.
    If `{persona_description}` is present in the prompt, it will:
      - Use the passed-in `persona` string, OR
      - Load `persona.txt` from the same directory
    """
    path = PROMPT_DIR / f"{name}.txt"

    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    prompt_string = path.read_text()

    persona_identifier_string = "{persona_description}"
    if persona_identifier_string in prompt_string:
        if persona is None:
            persona_path = PROMPT_DIR / "persona.txt"
            if not persona_path.exists():
                raise FileNotFoundError("persona.txt not found but required by prompt.")
            persona = persona_path.read_text().strip()

        prompt_string = prompt_string.replace(persona_identifier_string, persona)

    return prompt_string