import re

def parse_panel_story(full_story: str, panel_num: int) -> dict:
    """
    Parses full_story script text for a specific panel number (1-based).
    Extracts distinct caption, narration, and dialogue strings.
    """
    # Match panel block: [PANEL X] or PANEL X: or ## PANEL X
    pattern = rf"(?:\[PANEL\s*{panel_num}\]|PANEL\s*{panel_num}:?|##\s*PANEL\s*{panel_num})(.*?)(?=(?:\[PANEL\s*\d+\]|PANEL\s*\d+:?|##\s*PANEL\s*\d+)|$)"
    match = re.search(pattern, full_story, re.DOTALL | re.IGNORECASE)
    
    caption = ""
    narration = ""
    dialogue = ""
    
    if match:
        panel_block = match.group(1).strip()
        
        # Extract CAPTION (handles CAPTION:, **CAPTION:**, Caption:)
        cap_match = re.search(r"(?:\*\*|\#\#)?\s*CAPTION:\s*(?:\*\*|\#\#)?\s*(.*?)(?=(?:\*\*|\#\#)?\s*(?:NARRATION|DIALOGUE|TITLE):\s*|$)", panel_block, re.DOTALL | re.IGNORECASE)
        if cap_match:
            caption = cap_match.group(1).strip()
            
        # Extract NARRATION (handles NARRATION:, **NARRATION:**, Narration:)
        nar_match = re.search(r"(?:\*\*|\#\#)?\s*NARRATION:\s*(?:\*\*|\#\#)?\s*(.*?)(?=(?:\*\*|\#\#)?\s*(?:CAPTION|DIALOGUE|TITLE):\s*|$)", panel_block, re.DOTALL | re.IGNORECASE)
        if nar_match:
            narration = nar_match.group(1).strip()

        # Extract DIALOGUE (handles DIALOGUE:, **DIALOGUE:**, Dialogue:)
        dia_match = re.search(r"(?:\*\*|\#\#)?\s*DIALOGUE:\s*(?:\*\*|\#\#)?\s*(.*?)(?=(?:\*\*|\#\#)?\s*(?:CAPTION|NARRATION|TITLE):\s*|$)", panel_block, re.DOTALL | re.IGNORECASE)
        if dia_match:
            dialogue = dia_match.group(1).strip()

    # Fallback cleanup if headers were embedded without breaks
    caption = re.sub(r'^\*+|\*+$', '', caption).strip()
    narration = re.sub(r'^\*+|\*+$', '', narration).strip()
    dialogue = re.sub(r'^\*+|\*+$', '', dialogue).strip()

    return {
        "caption": caption,
        "narration": narration,
        "dialogue": dialogue
    }

def build_comic_layout(image_paths: list, full_story: str, outline: list) -> list:
    """
    Packages panel details, prompts, image paths, and story script into a clean dictionary list.
    Each item contains:
      - panel: int
      - title: str
      - scene_description: str
      - image_prompt: str
      - image_path: str
      - caption: str
      - narration: str
      - dialogue: str
    """
    layout = []
    
    for idx, panel_info in enumerate(outline):
        panel_num = panel_info.get("panel", idx + 1)
        img_path = image_paths[idx] if idx < len(image_paths) else ""
        
        story_details = parse_panel_story(full_story, panel_num)
        
        layout_item = {
            "panel": panel_num,
            "title": panel_info.get("title", f"Panel {panel_num}"),
            "scene_description": panel_info.get("scene_description", ""),
            "image_prompt": panel_info.get("image_prompt", ""),
            "image_path": img_path,
            "caption": story_details["caption"],
            "narration": story_details["narration"],
            "dialogue": story_details["dialogue"]
        }
        layout.append(layout_item)
        
    return layout
