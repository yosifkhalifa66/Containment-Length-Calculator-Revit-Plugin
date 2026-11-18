# Generate icon for the pyRevit button (32x32 PNG)
# Uses Pillow (PIL)
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(path, size=32):
    img = Image.new("RGBA", (size, size), (31, 55, 110, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw L-shaped conduit path (horizontal + vertical)
    line_color = (100, 200, 255, 255)
    draw.line([(6, 20), (20, 20)], fill=line_color, width=3)
    draw.line([(20, 20), (20, 6)], fill=line_color, width=3)
    
    # Arrow end markers
    draw.line([(6, 17), (6, 23)], fill=line_color, width=2)
    draw.line([(17, 6), (23, 6)], fill=line_color, width=2)
    
    # Ruler ticks
    tick_color = (200, 200, 200, 255)
    for x in [10, 14, 18]:
        draw.line([(x, 18), (x, 22)], fill=tick_color, width=1)
    
    # "L" label
    try:
        font = ImageFont.truetype("segoeui.ttf", 11)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 11)
        except:
            font = ImageFont.load_default()
    draw.text((22, 17), "L", fill=(255, 220, 100, 255), font=font)
    
    img.save(path)
    print("Created: " + path)


def create_dark_icon(path, size=32):
    img = Image.new("RGBA", (size, size), (40, 40, 45, 255))
    draw = ImageDraw.Draw(img)
    
    line_color = (80, 180, 255, 255)
    draw.line([(6, 20), (20, 20)], fill=line_color, width=3)
    draw.line([(20, 20), (20, 6)], fill=line_color, width=3)
    
    draw.line([(6, 17), (6, 23)], fill=line_color, width=2)
    draw.line([(17, 6), (23, 6)], fill=line_color, width=2)
    
    tick_color = (140, 140, 140, 255)
    for x in [10, 14, 18]:
        draw.line([(x, 18), (x, 22)], fill=tick_color, width=1)
    
    try:
        font = ImageFont.truetype("segoeui.ttf", 11)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 11)
        except:
            font = ImageFont.load_default()
    draw.text((22, 17), "L", fill=(255, 200, 80, 255), font=font)
    
    img.save(path)
    print("Created: " + path)


base = r"D:\AI Projects for Git\Containment Length Calculator Plugin\ContainmentLength.extension\Containment.tab\Length Tools.panel\Calculate Length.pushbutton"

create_icon(os.path.join(base, "icon.png"), 32)
create_dark_icon(os.path.join(base, "icon_dark.png"), 32)
print("Done!")
