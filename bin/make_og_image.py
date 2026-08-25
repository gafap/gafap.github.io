#!/usr/bin/env python3
"""Generate the link-preview banner and the iOS home-screen icon.

Both are derived from the light-mode profile photo, so both go stale together
when the photo or the job title changes. Run from the repo root:

    python bin/make_og_image.py

Writes:
    assets/img/og_preview.png      1200x630, the card LinkedIn/Bluesky/Slack show
    assets/img/apple_touch_icon.png  180x180, the iOS home-screen bookmark icon

Both paths are referenced from _config.yml (`og_image:` and `apple_touch_icon:`).
This script exists because the recipe used to live only in a commit message: a
later photo-tidying commit deleted og_preview.png while _config.yml still pointed
at it, so every page advertised an og:image that returned 404, and nothing in the
build noticed. Keep the recipe here, where it can be rerun.

The photo is square and the card is 1.91:1, so the photo cannot simply be used as
the card -- it would letterbox. Hence the composition: text panel beside a
full-bleed square crop, in the site's own colour tokens.
"""

from PIL import Image, ImageDraw, ImageFont

# Must match the tokens in assets/css/main.scss.
ACCENT = (9, 74, 131)  # --heading-accent, light mode
META = (85, 96, 110)  # --meta-color
TEXT = (26, 26, 26)
BG = (255, 255, 255)
RULE = (220, 224, 229)

# The light-mode photo from _pages/about.md (profile.image).
PHOTO = "assets/img/prof_pic2.jpg"

NAME_1 = "Gabriel A."
NAME_2 = "Facchini Palma"
ROLE = "Associate Professor of Economics"
INSTITUTION = "Royal Holloway, University of London"
FIELD = "Labour, health and development economics"  # keep in step with `description:` in _config.yml

FONTS = "C:/Windows/Fonts/%s"


def build_banner(width=1200, height=630):
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    photo = Image.open(PHOTO).convert("RGB").resize((height, height), Image.LANCZOS)
    img.paste(photo, (width - height, 0))
    draw.rectangle([0, 0, 10, height], fill=ACCENT)

    f_name = ImageFont.truetype(FONTS % "arialbd.ttf", 62)
    f_role = ImageFont.truetype(FONTS % "arial.ttf", 32)
    f_inst = ImageFont.truetype(FONTS % "arial.ttf", 28)
    f_field = ImageFont.truetype(FONTS % "arial.ttf", 26)

    x, y = 72, 150
    draw.text((x, y), NAME_1, font=f_name, fill=TEXT)
    draw.text((x, y + 74), NAME_2, font=f_name, fill=TEXT)
    draw.text((x, y + 178), ROLE, font=f_role, fill=ACCENT)
    draw.text((x, y + 224), INSTITUTION, font=f_inst, fill=META)
    draw.line([x, y + 288, x + 300, y + 288], fill=RULE, width=2)
    draw.text((x, y + 312), FIELD, font=f_field, fill=META)
    return img


def main():
    banner = build_banner()
    banner.save("assets/img/og_preview.png", "PNG", optimize=True)
    print("wrote assets/img/og_preview.png", banner.size)

    icon = Image.open(PHOTO).convert("RGB").resize((180, 180), Image.LANCZOS)
    icon.save("assets/img/apple_touch_icon.png", "PNG", optimize=True)
    print("wrote assets/img/apple_touch_icon.png", icon.size)


if __name__ == "__main__":
    main()
