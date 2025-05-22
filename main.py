from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps
import io

app = FastAPI()

def apply_to_tshirt(tshirt_path, mask_path, overlay_file):
    tshirt = Image.open(tshirt_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")
    overlay = Image.open(overlay_file).convert("RGBA")

    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError("マスクに白い領域がありません")

    left, top, right, bottom = bbox
    target_w = right - left
    target_h = bottom - top

    # ★ここがキモ
    resized_overlay = ImageOps.contain(overlay, (target_w, target_h), method=Image.LANCZOS)

    offset_x = left + (target_w - resized_overlay.width) // 2
    offset_y = top + (target_h - resized_overlay.height) // 2 + 130  # 必要に応じて調整

    result = tshirt.copy()
    result.paste(resized_overlay, (offset_x, offset_y), resized_overlay)

    return result

@app.post("/mock")
async def generate_mock(overlay: UploadFile = File(...)):
    output_img = apply_to_tshirt("images/tshirt.png", "images/mask.png", overlay.file)

    buffer = io.BytesIO()
    output_img.save(buffer, format="PNG")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")
