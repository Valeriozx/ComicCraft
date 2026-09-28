from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

router = APIRouter()

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

class GenerateComicRequest(BaseModel):
    prompt: str
    character_name: str = "Hero"
    setting: str = "Futuristic City"
    tone: str = "Action-packed"
    art_style: str = "Comic Book"

@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Renders the main creation form page."""
    return templates.TemplateResponse(request=request, name="index.html", context={})

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic_form(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form("Hero"),
    setting: str = Form("Cyberpunk Metropolis"),
    tone: str = Form("Dramatic"),
    art_style: str = Form("Comic Book")
):
    """
    Form handler endpoint. Runs the full AI pipeline:
    1. Gemini Flash -> 5-panel outline
    2. Gemini Pro -> Full story script
    3. Image Generator -> Panel PNG images
    4. Layout Builder -> Packaged panel layout
    5. Exporters -> PDF file
    Renders comic_preview.html.
    """
    try:
        # Step 1: Outline
        outline = generate_outline(prompt)

        # Step 2: Story Script
        full_story = generate_story(
            outline=outline,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )

        # Step 3: Images
        image_paths = []
        for panel in outline:
            panel_prompt = f"{panel.get('image_prompt', '')}, {art_style} style"
            img_path = generate_image(panel_prompt)
            image_paths.append(img_path)

        # Step 4: Layout Assembly
        layout = build_comic_layout(image_paths, full_story, outline)

        # Step 5: Export PDF
        pdf_url = save_pdf(layout)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": pdf_url,
                "prompt": prompt,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "art_style": art_style
            }
        )
    except Exception as e:
        print(f"[Routes Error] Exception during generation: {e}")
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Failed to generate comic: {str(e)}",
                "prompt": prompt,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "art_style": art_style
            }
        )

@router.post("/generate-comic/json")
async def generate_comic_json(payload: GenerateComicRequest):
    """
    API endpoint returning structured comic layout and PDF link as JSON.
    """
    try:
        outline = generate_outline(payload.prompt)
        full_story = generate_story(
            outline=outline,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style
        )
        
        image_paths = []
        for panel in outline:
            panel_prompt = f"{panel.get('image_prompt', '')}, {payload.art_style} style"
            img_path = generate_image(panel_prompt)
            image_paths.append(img_path)

        layout = build_comic_layout(image_paths, full_story, outline)
        pdf_url = save_pdf(layout)

        return JSONResponse(
            content={
                "status": "success",
                "layout": layout,
                "pdf_url": pdf_url
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_url: str = ""):
    """Renders export completion page."""
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf_url": pdf_url}
    )
