"""Create a temporary 128x384 portrait sheet from the winter walk sprite."""

from __future__ import annotations

import os

from PIL import Image


PORTRAIT_SIZE = 64
COLUMNS = 2
ROWS = 6


def main() -> None:
    sprite_path = os.environ.get(
        "SPRITE_PATH",
        os.path.join(os.environ["MOD_ROOT"], "asset", "sprites", "blade_winter.png"),
    )
    output_path = os.environ.get(
        "PORTRAIT_PATH",
        os.path.join(os.environ["MOD_ROOT"], "asset", "portrait", "blade.png"),
    )
    preview_path = os.environ.get(
        "PREVIEW_PATH",
        os.path.join(os.environ["MOD_ROOT"], "asset", "_source", "portrait_preview.png"),
    )

    sprite = Image.open(sprite_path).convert("RGBA")
    # The first 16x16 cell contains the front-facing head and shoulders.
    head = sprite.crop((0, 0, 16, 16)).resize(
        (PORTRAIT_SIZE, PORTRAIT_SIZE), Image.Resampling.NEAREST
    )

    sheet = Image.new("RGBA", (PORTRAIT_SIZE * COLUMNS, PORTRAIT_SIZE * ROWS), (0, 0, 0, 0))
    for row in range(ROWS):
        for col in range(COLUMNS):
            sheet.alpha_composite(head, (col * PORTRAIT_SIZE, row * PORTRAIT_SIZE))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(preview_path), exist_ok=True)
    sheet.save(output_path)
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.Resampling.NEAREST).save(preview_path)
    print(f"saved {output_path} ({sheet.width}x{sheet.height})")
    print(f"preview {preview_path}")


if __name__ == "__main__":
    main()
