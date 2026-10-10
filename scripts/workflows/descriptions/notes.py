"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

KEY_STEP = "1. Set your key in **ComfyUI menu → Extensions → BytePlus → BytePlus settings**.\n"

WORKFLOW_TEXTS = {
    "chat-01-write-a-product-listing": {
        "input": (
            KEY_STEP + "2. Describe your product in **Product**.\n"
            "3. In **Chat: Attach Document**, choose its spec sheet: a PDF or text file at the top of ComfyUI's input "
            "folder. Press R if it is not listed.\n"
            "4. Press **Run**. The listing is saved as JSON under `text/byteplus`.\n\n"
            "Models: Seedream 5.0 flash and Seed 2.0 lite. Activate them on ModelArk's **Model activation** page."
        ),
        "photo": (
            "Seedream 5.0 flash draws a square product photo from **Product**. To use your own photo, add **Load "
            "Image** and connect it to **Write**'s **image** instead."
        ),
        "photo_description": "Draws the product photo.",
        "write": (
            "Seed 2.0 lite reads the photo and the spec sheet in one request, with thinking off, and writes the "
            "listing as JSON: a title, five bullet points, and a short description. The answer schema makes it answer "
            "in exactly that shape. **Write** shows the listing and saves it.\n\n"
            "Open **Write** to change the instructions or the schema."
        ),
        "write_description": "Writes the listing from the photo and the spec sheet, as JSON, and saves it.",
    },
    "chat-02-summarize-a-voice-note": {
        "input": (
            KEY_STEP + "2. Upload a voice note in **Voice Note**: a recording of up to a few minutes.\n"
            "3. Press **Run**. The transcript and the action items are saved under `text/byteplus`.\n\n"
            "Models: Seed 2.0 mini, which reads audio, and Dola Seed 2.1 turbo. Activate them on ModelArk's **Model "
            "activation** page."
        ),
        "transcribe": (
            "Seed 2.0 mini listens to the voice note and writes what is said, word for word, with thinking off. "
            "**Transcribe** shows the transcript and saves it."
        ),
        "transcribe_description": "Transcribes the voice note and saves the transcript.",
        "actions": (
            "Dola Seed 2.1 turbo continues the same conversation: **conversation** carries the transcript, so the "
            "audio is not sent again. It lists every action item and sums up the note, and **Action Items** saves the "
            "list.\n\n"
            "**Request Options** sends this request at the flex tier, which BytePlus runs in a low-priority queue at a "
            "lower rate, so the answer can take several minutes. Only a few models take flex; **Model: Info** shows "
            '`"flex": true` for them.'
        ),
        "actions_description": "Lists the action items from the transcript and saves them.",
    },
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
            KEY_STEP + '2. Describe the series in **Brief**, starting with how many, such as "Generate 4 posters".\n'
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
