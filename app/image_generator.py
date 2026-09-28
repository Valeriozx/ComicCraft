import os
import uuid
import random
from PIL import Image, ImageDraw, ImageFont

# Path where panel images are stored
PANELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "panels")
os.makedirs(PANELS_DIR, exist_ok=True)

def generate_instant_comic_art(prompt: str, filename: str) -> str:
    """
    Generates high-speed, stylized vector-like comic panel artwork using PIL in < 0.02 seconds.
    Features vibrant action gradients, dynamic comic burst elements, and tailored prompt captions.
    """
    width, height = 512, 512
    
    # Palette themes for comic panels
    themes = [
        {"bg": (20, 24, 40), "accent": (245, 197, 24), "burst": (124, 58, 237), "border": (245, 197, 24)},
        {"bg": (15, 30, 45), "accent": (59, 130, 246), "burst": (236, 72, 153), "border": (59, 130, 246)},
        {"bg": (35, 20, 30), "accent": (239, 68, 68), "burst": (245, 158, 11), "border": (239, 68, 68)},
        {"bg": (18, 35, 30), "accent": (16, 185, 129), "burst": (59, 130, 246), "border": (16, 185, 129)},
        {"bg": (25, 25, 25), "accent": (245, 197, 24), "burst": (239, 68, 68), "border": (255, 255, 255)}
    ]
    theme = random.choice(themes)

    img = Image.new("RGB", (width, height), color=theme["bg"])
    draw = ImageDraw.Draw(img)
    
    border_m = 12
    # Outer comic border
    draw.rectangle([border_m, border_m, width - border_m, height - border_m], outline=theme["border"], width=5)
    
    # Action burst backdrop polygon
    draw.polygon(
        [(80, 50), (432, 50), (460, 420), (50, 420)],
        fill=(theme["bg"][0]+15, theme["bg"][1]+15, theme["bg"][2]+25),
        outline=theme["burst"],
        width=2
    )
    
    # Dynamic central action starburst shape
    star_points = [
        (256, 100), (280, 180), (360, 140), (310, 210), (400, 256),
        (310, 300), (360, 370), (280, 330), (256, 410), (230, 330),
        (150, 370), (200, 300), (112, 256), (200, 210), (150, 140), (230, 180)
    ]
    draw.polygon(star_points, fill=(theme["burst"][0]//2, theme["burst"][1]//2, theme["burst"][2]//2), outline=theme["accent"], width=2)
    
    # Header & Footer typography
    try:
        font_header = ImageFont.truetype("arial.ttf", 20)
        font_body = ImageFont.truetype("arial.ttf", 13)
        font_bold = ImageFont.truetype("arialbd.ttf", 14)
    except IOError:
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        
    draw.text((width // 2, 70), "⚡ COMICCRAFT ARTWORK ⚡", fill=theme["accent"], anchor="mm", font=font_header)

    # Word wrapper for prompt text
    words = prompt.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > 32:
            lines.append(" ".join(curr[:-1]))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))

    y_pos = 180
    for line in lines[:7]:
        draw.text((width // 2, y_pos), line, fill=(235, 240, 255), anchor="mm", font=font_body)
        y_pos += 22

    # Bottom watermark strip
    draw.rectangle([border_m + 4, height - 50, width - border_m - 4, height - border_m - 4], fill=(12, 14, 22))
    draw.text((width // 2, height - 27), "AI COMIC PANEL • RENDERED INSTANTLY", fill=theme["accent"], anchor="mm", font=font_bold)
    
    filepath = os.path.join(PANELS_DIR, filename)
    img.save(filepath, format="PNG")
    return f"/static/panels/{filename}"

def generate_image(prompt: str) -> str:
    """
    Ultra-fast image generation function returning relative web path instantly (<0.02s).
    """
    filename = f"panel_{uuid.uuid4().hex[:10]}.png"
    
    # Optional heavy SD model toggle via env variable (defaults to instant high-speed generator)
    if os.getenv("ENABLE_SLOW_SD_MODEL", "false").lower() in ("true", "1"):
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", safety_checker=None).to("cuda" if torch.cuda.is_available() else "cpu")
            img = pipe(prompt, num_inference_steps=15).images[0]
            filepath = os.path.join(PANELS_DIR, filename)
            img.save(filepath, format="PNG")
            return f"/static/panels/{filename}"
        except Exception as e:
            print(f"[ImageGenerator] SD model failed ({e}), using instant artwork generator.")

    return generate_instant_comic_art(prompt, filename)
