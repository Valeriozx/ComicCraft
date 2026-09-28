import os
import concurrent.futures
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def _call_gemini_pro_api(prompt: str) -> str | None:
    model_names = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-pro-latest"]
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt, generation_config={"temperature": 0.8})
            if response and response.text:
                return response.text.strip()
        except Exception:
            continue
    return None

def generate_story(outline: list, character_name: str, setting: str, tone: str, art_style: str) -> str:
    """
    Generates a detailed comic script using Gemini Pro instantly.
    Uses fast API call with a strict short timeout, falling back immediately to instant custom story engine.
    """
    outline_str = "\n".join([
        f"Panel {p.get('panel', idx+1)}: [{p.get('title', '')}] - {p.get('scene_description', '')}"
        for idx, p in enumerate(outline)
    ])

    prompt = (
        f"Write a 5-panel comic script for Protagonist: {character_name}, Setting: {setting}, Tone: {tone}, Style: {art_style}.\n"
        f"Panels:\n{outline_str}\n\n"
        f"Format strictly per panel:\n"
        f"[PANEL X]\nTITLE: <Title>\nCAPTION: <Caption>\nNARRATION: <Narration>\nDIALOGUE: {character_name}: \"<Speech>\"\n"
    )

    if GEMINI_API_KEY:
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_call_gemini_pro_api, prompt)
                story_text = future.result(timeout=1.2)  # Strict 1.2s timeout for instant speed
                if story_text:
                    return story_text
        except Exception:
            pass

    # Instant Custom 5-Panel Comic Script Generator with unique progressing storylines
    script_blocks = []
    
    dialogues = [
        f"{character_name}: \"Something isn't right here in {setting}... I can feel it.\"",
        f"{character_name}: \"There it is! But time is running out!\"",
        f"{character_name}: \"Hold on! I won't let everything fall apart now!\"",
        f"{character_name}: \"This ends right here, right now!\"",
        f"{character_name}: \"It's over... {setting} is finally safe once more.\""
    ]
    
    captions = [
        f"{setting} — 08:00 HRS. Tone: {tone}.",
        f"Deep within {setting}. Conflict escalates.",
        f"Moments later. High stakes ahead.",
        f"The climax of the confrontation.",
        f"The aftermath in {setting}."
    ]

    for idx, panel in enumerate(outline[:5]):
        p_num = panel.get("panel", idx + 1)
        p_title = panel.get("title", f"Panel {p_num}")
        p_desc = panel.get("scene_description", "")
        
        dialogue_line = dialogues[idx] if idx < len(dialogues) else f"{character_name}: \"We keep moving forward!\""
        caption_line = captions[idx] if idx < len(captions) else f"{setting}."
        
        block = (
            f"[PANEL {p_num}]\n"
            f"TITLE: {p_title}\n"
            f"CAPTION: {caption_line}\n"
            f"NARRATION: {character_name} stands amidst {setting}. {p_desc}\n"
            f"DIALOGUE: {dialogue_line}"
        )
        script_blocks.append(block)

    return "\n\n".join(script_blocks)
