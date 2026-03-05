"""Generate PNG icons from the source SVG for PWA and app stores.

Requirements: pip install Pillow cairosvg
Usage:        python app/static/icons/generate_icons.py
"""

from pathlib import Path

import cairosvg
from PIL import Image
import io

ICONS_DIR = Path(__file__).parent
SVG_PATH = ICONS_DIR / "icon.svg"

SIZES = {
    "icon-192.png": 192,
    "icon-512.png": 512,
    "apple-touch-icon.png": 180,
}


def generate():
    svg_data = SVG_PATH.read_bytes()

    for filename, size in SIZES.items():
        png_data = cairosvg.svg2png(bytestring=svg_data, output_width=size, output_height=size)
        out = ICONS_DIR / filename
        out.write_bytes(png_data)
        print(f"  {out} ({size}x{size})")

    # favicon.ico — 32x32 and 16x16 packed into one .ico
    ico_sizes = [32, 16]
    images = []
    for s in ico_sizes:
        png_data = cairosvg.svg2png(bytestring=svg_data, output_width=s, output_height=s)
        images.append(Image.open(io.BytesIO(png_data)))
    ico_path = ICONS_DIR / "favicon.ico"
    images[0].save(ico_path, format="ICO", sizes=[(s, s) for s in ico_sizes], append_images=images[1:])
    print(f"  {ico_path} (multi-size ico)")


if __name__ == "__main__":
    print("Generating icons...")
    generate()
    print("Done!")
