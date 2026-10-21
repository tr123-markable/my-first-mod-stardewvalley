"""Build four seasonal 64x128 NPC walk sheets from the layered PSD template."""

from __future__ import annotations

import os
from collections import deque

import numpy as np
from PIL import Image, ImageDraw
from psd_tools import PSDImage


SPRITE_W = 64
SPRITE_H = 128
FRAME_W = 16
FRAME_H = 32


PALETTES = {
    "spring": {
        "shirt": (247, 239, 220),
        "shirt_shadow": (213, 198, 171),
        "pants": (26, 31, 36),
        "pants_shadow": (67, 76, 84),
        "accent": (132, 24, 32),
        "accent2": (208, 166, 76),
        "trim": "collar",
        "trim_color": (208, 166, 76),
    },
    "summer": {
        "shirt": (224, 236, 245),
        "shirt_shadow": (172, 192, 207),
        "pants": (38, 47, 57),
        "pants_shadow": (91, 105, 117),
        "accent": (168, 36, 36),
        "accent2": (226, 233, 240),
        "trim": "waist",
        "trim_color": (168, 36, 36),
    },
    "fall": {
        "shirt": (102, 46, 58),
        "shirt_shadow": (66, 28, 38),
        "pants": (31, 24, 27),
        "pants_shadow": (80, 62, 58),
        "accent": (184, 85, 44),
        "accent2": (218, 171, 75),
        "trim": "waist",
        "trim_color": (218, 171, 75),
    },
    "winter": {
        "shirt": (74, 86, 104),
        "shirt_shadow": (46, 55, 69),
        "pants": (24, 29, 40),
        "pants_shadow": (65, 76, 91),
        "accent": (142, 31, 45),
        "accent2": (159, 195, 221),
        "trim": "scarf",
        "trim_color": (244, 247, 250),
    },
}


def remove_white_background(image: Image.Image) -> Image.Image:
    """Make the connected white canvas transparent while keeping enclosed highlights."""
    arr = np.array(image.convert("RGBA"))
    height, width = arr.shape[:2]
    visited = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    def is_canvas_white(y: int, x: int) -> bool:
        r, g, b, a = arr[y, x]
        return bool(a > 0 and min(r, g, b) >= 246 and max(r, g, b) - min(r, g, b) <= 5)

    for x in range(width):
        for y in (0, height - 1):
            if not visited[y, x] and is_canvas_white(y, x):
                visited[y, x] = True
                queue.append((y, x))
    for y in range(height):
        for x in (0, width - 1):
            if not visited[y, x] and is_canvas_white(y, x):
                visited[y, x] = True
                queue.append((y, x))

    while queue:
        y, x = queue.popleft()
        arr[y, x, 3] = 0
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and not visited[ny, nx]:
                if is_canvas_white(ny, nx):
                    visited[ny, nx] = True
                    queue.append((ny, nx))

    # Stardew NPC sheets are pixel art; drop soft alpha fringes to avoid white halos.
    arr[arr[:, :, 3] < 128] = 0
    arr[arr[:, :, 3] >= 128, 3] = 255
    arr[arr[:, :, 3] == 0, :3] = 0
    return Image.fromarray(arr, "RGBA")


def build_clean_walk_sheet(source: Image.Image) -> Image.Image:
    """Use the four main PSD rows and mirror the right-facing row for the left-facing row."""
    sheet = Image.new("RGBA", (SPRITE_W, SPRITE_H), (0, 0, 0, 0))
    sheet.paste(source.crop((0, 0, SPRITE_W, FRAME_H)), (0, 0))
    sheet.paste(source.crop((0, FRAME_H, SPRITE_W, FRAME_H * 2)), (0, FRAME_H))
    sheet.paste(source.crop((0, FRAME_H * 2, SPRITE_W, FRAME_H * 3)), (0, FRAME_H * 2))
    right = source.crop((0, FRAME_H, SPRITE_W, FRAME_H * 2))
    sheet.paste(right.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (0, FRAME_H * 3))
    return sheet


def recolor_sheet(base: Image.Image, palette: dict) -> Image.Image:
    arr = np.array(base.convert("RGBA"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    a = arr[:, :, 3]
    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)

    shirt = (a > 0) & (r >= 240) & (g >= 230) & (b >= 190) & (b <= 240) & (g >= b + 8)
    pants = (a > 0) & (
        (maxc <= 42)
        | ((minc >= 84) & (maxc <= 122) & ((maxc - minc) < 14))
    )
    red_accent = (a > 0) & (r >= 90) & (g < 80) & (b < 80) & (r > g * 2 + 20) & (r > b * 2 + 20)
    gold_accent = (a > 0) & (r >= 200) & (g >= 150) & (b < 100)

    # Keep the original dark hair and outlines; restrict pants edits to the lower body.
    local_y = np.tile(np.arange(SPRITE_H) % FRAME_H, (SPRITE_W, 1)).T
    pants &= local_y >= 21

    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    shirt_base = shirt & (luminance >= 238)
    shirt_shadow = shirt & ~shirt_base
    pants_base = pants & (luminance < 80)
    pants_shadow = pants & ~pants_base

    arr[shirt_base] = (*palette["shirt"], 255)
    arr[shirt_shadow] = (*palette["shirt_shadow"], 255)
    arr[pants_base] = (*palette["pants"], 255)
    arr[pants_shadow] = (*palette["pants_shadow"], 255)
    arr[red_accent] = (*palette["accent"], 255)
    arr[gold_accent] = (*palette["accent2"], 255)

    # Add a simple season-specific garment trim without changing the frame layout.
    for row in range(SPRITE_H // FRAME_H):
        for col in range(SPRITE_W // FRAME_W):
            y0 = row * FRAME_H
            x0 = col * FRAME_W
            frame_shirt = shirt[y0 : y0 + FRAME_H, x0 : x0 + FRAME_W]
            ys, xs = np.nonzero(frame_shirt)
            if len(ys) == 0:
                continue
            if palette["trim"] == "scarf":
                edge = ys <= ys.min() + 1
            else:
                edge = ys >= ys.max() - 1
            for ly, lx in zip(ys[edge], xs[edge]):
                arr[y0 + ly, x0 + lx, :3] = palette["trim_color"]
                arr[y0 + ly, x0 + lx, 3] = 255

    return Image.fromarray(arr, "RGBA")


def make_preview(sheets: dict[str, Image.Image]) -> Image.Image:
    scale = 4
    margin = 8
    label_h = 18
    width = len(sheets) * (SPRITE_W * scale + margin) + margin
    height = label_h + SPRITE_H * scale + margin
    preview = Image.new("RGB", (width, height), (244, 241, 234))
    draw = ImageDraw.Draw(preview)
    for index, (name, sheet) in enumerate(sheets.items()):
        x = margin + index * (SPRITE_W * scale + margin)
        draw.text((x, 3), name.upper(), fill=(35, 35, 40))
        scaled = sheet.resize((SPRITE_W * scale, SPRITE_H * scale), Image.Resampling.NEAREST)
        preview.paste(scaled, (x, label_h), scaled)
    return preview


def main() -> None:
    psd_path = os.environ["PSD_PATH"]
    out_dir = os.environ["OUT_DIR"]
    preview_dir = os.environ.get("PREVIEW_DIR", out_dir)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    psd = PSDImage.open(psd_path)
    for layer in psd:
        if layer.name in {"背景", "范围"}:
            layer.visible = False
    raw = psd.composite(ignore_preview=True).convert("RGBA")
    transparent = remove_white_background(raw)
    clean = build_clean_walk_sheet(transparent)

    clean.save(os.path.join(preview_dir, "blade_base_clean.png"))
    sheets = {}
    for season, palette in PALETTES.items():
        sheet = recolor_sheet(clean, palette)
        sheet.save(os.path.join(out_dir, f"blade_{season}.png"))
        sheets[season] = sheet

    make_preview(sheets).save(os.path.join(preview_dir, "preview_seasons.png"))
    print("saved:", ", ".join(f"blade_{season}.png" for season in PALETTES))


if __name__ == "__main__":
    main()
