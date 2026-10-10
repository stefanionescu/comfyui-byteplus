"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

KEY_STEP = "1. Set your key in **ComfyUI menu → Extensions → BytePlus → BytePlus settings**.\n"

WORKFLOW_TEXTS = {
    "image-01-design-a-character": {
        "input": (
            KEY_STEP + "2. Describe your character in **Character**: who they are, what they wear, and what they "
            "carry.\n"
            "3. Press **Run**. Both images are saved under `image/byteplus`.\n\n"
            "Model: Seedream 5.0 flash. Activate it on ModelArk's **Model activation** page."
        ),
        "design": (
            "Seedream 5.0 flash draws the character in full, from the front, at 3:4. Its **references** carry the "
            "image's own ModelArk address on to **Wave**."
        ),
        "sheet_description": "Draws the character and saves the image.",
        "wave": (
            "Seedream 5.0 flash edits the character from its address, keeping the outfit, and draws it waving. "
            "Change the prompt in **Wave** to pose the character another way.\n\n"
            "The address works for 24 hours; after that, open **Sheet** and change **run number** to draw the "
            "character again."
        ),
        "wave_description": "Draws the same character waving and saves the image.",
    },
    "image-02-make-a-poster-series": {
        "input": (
            KEY_STEP + "2. Describe the series in **Brief**: what each poster shows and what they share.\n"
            "3. Press **Run**. Up to four posters are saved under `image/byteplus`.\n\n"
            "Model: Seedream 4.0. Activate it on ModelArk's **Model activation** page."
        ),
        "model": (
            "**Model** holds the model **Series** uses. **Model: Info** shows what the extension knows about it, for "
            "free and without the key, and **Info** shows it as JSON. Seedream 4.0 makes a series of related images "
            "in one request, so **count** can be 4. The default, Seedream 5.0 flash, makes one image per request, so "
            "the node refuses a count of 4 for it before sending anything."
        ),
        "series": (
            "Seedream 4.0 draws the posters as one series, so the style and the typeface match. It decides how many "
            "to make, up to the four **count** allows, and each poster it makes is billed."
        ),
        "series_description": "Draws the poster series and saves it.",
    },
    "image-03-split-a-poster-into-layers": {
        "input": (
            KEY_STEP + "2. Describe the poster in **Poster**. Put any words it shows in quotation marks.\n"
            "3. Press **Run**. The poster and each layer are saved under `image/byteplus`.\n\n"
            "Model: Seedream 5.0 flash. Activate it on ModelArk's **Model activation** page."
        ),
        "draw": (
            "Seedream 5.0 flash draws the poster at 3:4 as a PNG. Its **references** carry the poster's own address "
            "on to **Split**."
        ),
        "draw_description": "Draws the poster and saves it.",
        "split": (
            "Seedream 5.0 flash splits the poster into separate layers, such as the title, the lanterns, and the "
            "date. **Join Image with Alpha** gives each layer its transparency, and the layers are saved as PNG "
            "files, each at its place on a canvas the size of the poster. Each layer is billed as one image."
        ),
        "split_description": "Splits the poster into transparent layers and saves them.",
    },
}

__all__ = ["WORKFLOW_TEXTS"]
