"""Build the Flower Dance sprite sheet from the PSD's special-action row."""

from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image
from psd_tools import PSDImage

sys.path.insert(0, os.path.dirname(__file__))
from make_seasonal_sprites import remove_white_background


def main() -> None:
    root = os.environ["MOD_ROOT"]
    psd_path = os.path.join(root, "asset", "_source", "walk_template.psd")
    spring_path = os.path.join(root, "asset", "sprites", "blade_spring.png")
    output_path = os.path.join(root, "asset", "sprites", "blade_flowerdance.png")
    preview_path = os.path.join(root, "asset", "_source", "preview_flowerdance.png")

    psd = PSDImage.open(psd_path)
    for layer in psd:
        layer.visible = layer.name == "11（花舞节"

    raw = psd.composite(ignore_preview=True).convert("RGBA")
    dance = remove_white_background(raw.crop((0, 352, 64, 384)))

    # The PSD special-action row is a brown-haired template. Recolor only the
    # dark hair pixels so the placeholder matches Blade's palette.
    arr = np.array(dance)
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    a = arr[:, :, 3]
    hair = (
        (a > 0)
        & (np.arange(32)[:, None] < 15)
        & (r > 35)
        & (r < 180)
        & (g > 25)
        & (g < 145)
        & (b > 15)
        & (b < 125)
        & (r >= g)
        & (g >= b)
    )
    arr[hair, :3] = (22, 2, 68)

    # A few red tips keep the special pose visually tied to Blade's base sheet.
    local_x = np.tile(np.arange(64) % 16, (32, 1))
    arr[hair & (local_x < 2) & (np.arange(32)[:, None] > 8), :3] = (124, 0, 0)
    arr[hair & (local_x > 13) & (np.arange(32)[:, None] > 8), :3] = (124, 0, 0)

    dance = Image.fromarray(arr, "RGBA")
    spring = Image.open(spring_path).convert("RGBA")
    sheet = Image.new("RGBA", (64, 160), (0, 0, 0, 0))
    sheet.paste(spring, (0, 0))
    sheet.paste(dance, (0, 128))
    sheet.save(output_path)

    preview = sheet.resize((256, 640), Image.Resampling.NEAREST)
    preview.save(preview_path)
    print("saved", output_path)
    print("preview", preview_path)


if __name__ == "__main__":
    main()
