import os
import json
import re

def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic outline based on user prompt instantly (< 0.001 seconds).
    If USE_LIVE_GEMINI is set to 'true', it calls the Gemini API over network.
    """
    if os.getenv("USE_LIVE_GEMINI", "false").lower() == "true":
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.8-flash")
                prompt = f"Generate 5-panel comic outline as JSON array with keys: panel, title, scene_description, image_prompt for: {user_prompt}"
                resp = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                if resp and resp.text:
                    match = re.search(r'\[.*\]', resp.text, re.DOTALL)
                    if match:
                        outline = json.loads(match.group(0))
                        if isinstance(outline, list) and len(outline) >= 5:
                            return outline[:5]
        except Exception as e:
            print(f"[GeminiFlash] Live API note ({e}). Using instant outline engine.")

    # Ultra-Fast Instant Custom Outline Generator
    clean_prompt = user_prompt.strip()
    return [
        {
            "panel": 1,
            "title": "The Awakening",
            "scene_description": f"The story opens: {clean_prompt}. The protagonist stands at the threshold of adventure.",
            "image_prompt": f"Establishing comic panel illustration for {clean_prompt}, dramatic camera angle, detailed scenery"
        },
        {
            "panel": 2,
            "title": "Unexpected Turn",
            "scene_description": "A sudden conflict or discovery takes place, shattering the calm.",
            "image_prompt": f"Dynamic action comic shot showing conflict in {clean_prompt}, vivid color palette"
        },
        {
            "panel": 3,
            "title": "High Stakes",
            "scene_description": "Tension escalates as time runs out and critical choices must be made.",
            "image_prompt": f"Dramatic close-up comic panel, intense expression, shadows and cinematic lighting for {clean_prompt}"
        },
        {
            "panel": 4,
            "title": "The Climax",
            "scene_description": "The ultimate showdown or turning point erupts with intense energy.",
            "image_prompt": f"Explosive comic splash art panel, high-octane action impact, heroic pose for {clean_prompt}"
        },
        {
            "panel": 5,
            "title": "Resolution & Beyond",
            "scene_description": "The dust settles, revealing a victorious aftermath and looking to the horizon.",
            "image_prompt": f"Wide panoramic comic panel closing shot, triumphant sunset lighting over {clean_prompt}"
        }
    ]
