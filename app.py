# AutoPassPhoto - Created by @vahidzahani
# This script processes an input photo by removing the background,
# resizing it to passport size (3x4 cm), arranging it on a 13x18 cm sheet,
# adding borders, watermark, and exporting as high-quality JPEG images.

from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from rembg import remove
import io, json

# Constants
DPI = 300
PHOTO_CM = (3, 4)
SHEET_CM = (13, 18)
GAP_CM = 0.1
MARGIN_CM = 0.5
TEXT_MARGIN_CM = 0.3
FONT_PATH = "cour.ttf"

# Convert cm to pixels
def cm_to_px(cm):
    return int((cm / 2.54) * DPI)

# Step 1: Remove background
def remove_background(image_path):
    with open(image_path, "rb") as f:
        input_data = f.read()
    output_data = remove(input_data)
    img_rgba = Image.open(io.BytesIO(output_data)).convert("RGBA")
    return img_rgba

# Step 2: Place on white background
def place_on_white(img_rgba):
    bg_white = Image.new("RGB", img_rgba.size, "white")
    bg_white.paste(img_rgba, mask=img_rgba.split()[3])
    return bg_white

# Step 3: Enhance image quality
def enhance_image(img):
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    img = ImageEnhance.Brightness(img).enhance(1.05)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Color(img).enhance(1.1)
    return img

# Step 4: Resize to 3x4 cm
def resize_to_passport(img):
    width, height = cm_to_px(PHOTO_CM[0]), cm_to_px(PHOTO_CM[1])
    return img.resize((width, height), Image.LANCZOS)

# Step 5: Create 13x18 cm sheet and arrange photos
def create_sheet(photo):
    photo_w, photo_h = photo.size
    sheet_w, sheet_h = cm_to_px(SHEET_CM[0]), cm_to_px(SHEET_CM[1])
    gap = cm_to_px(GAP_CM)
    margin_x = cm_to_px(MARGIN_CM)
    margin_y = cm_to_px(MARGIN_CM)

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)

    x_count = (sheet_w - margin_x + gap) // (photo_w + gap)
    y_count = (sheet_h - margin_y + gap) // (photo_h + gap)

    for i in range(int(x_count)):
        for j in range(int(y_count)):
            x = margin_x + i * (photo_w + gap)
            y = margin_y + j * (photo_h + gap)
            if x + photo_w <= sheet_w and y + photo_h <= sheet_h:
                sheet.paste(photo, (int(x), int(y)))
                draw.rectangle(
                    [x, y, x + photo_w - 1, y + photo_h - 1], 
                    outline=(150, 150, 150), width=2
                )
    return sheet

# Step 6: Add watermark text to the sheet
def add_watermark(sheet):
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(FONT_PATH, size=cm_to_px(0.3))
    except:
        font = ImageFont.load_default()

    text = "Create BY : github.com/vahidzahani"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x_text = cm_to_px(TEXT_MARGIN_CM)
    y_text = sheet.height - text_h - cm_to_px(TEXT_MARGIN_CM)

    txt_img = Image.new("RGBA", sheet.size, (255,255,255,0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((x_text, y_text), text, font=font, fill=(0,0,0,120))

    return Image.alpha_composite(sheet.convert("RGBA"), txt_img).convert("RGB")

# Step 7: Save output files
def save_outputs(photo, sheet):
    photo.save("photo_3x4.jpg", dpi=(DPI, DPI), quality=95)
    sheet.save("photo_13x18.jpg", dpi=(DPI, DPI), quality=95)

# Step 8: Main process
if __name__ == "__main__":
    try:
        rgba = remove_background("input.jpg")
        white_bg = place_on_white(rgba)
        enhanced = enhance_image(white_bg)
        resized = resize_to_passport(enhanced)
        sheet = create_sheet(resized)
        final_sheet = add_watermark(sheet)
        save_outputs(resized, final_sheet)

        output = {
            "status": "success",
            "message": "Processing completed.",
            "outputs": [
                "photo_3x4.jpg",
                "photo_13x18.jpg"
            ]
        }
    except Exception as e:
        output = {
            "status": "error",
            "message": str(e)
        }

    print(json.dumps(output, indent=2))
