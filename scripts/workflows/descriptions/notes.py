"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

KEY_STEP = "1. Set your key in **ComfyUI menu → Extensions → BytePlus → BytePlus settings**.\n"
RECOVER_STEP = (
    "ModelArk usually starts the task at once, so a cancelled run's video is still made and billed; collect it with "
    "**video-05-recover-a-video**."
)

WORKFLOW_TEXTS = {
    "chat-01-write-a-product-listing": {
        "input": (
            KEY_STEP + "2. Describe your product in **Product**.\n"
            "3. In **Chat: Attach Document**, choose its spec sheet: a PDF or text file at the top of ComfyUI's input "
            "folder.\n"
            "4. Press **Run**. The listing is saved as JSON under `text/byteplus`."
        ),
        "photo": (
            "Seedream 5.0 flash draws a square product photo from **Product**. To use your own photo, add **Load "
            "Image** and connect it to **Write**'s **image** instead."
        ),
        "photo_description": "Draws the product photo.",
        "write": (
            "Seed 2.0 lite reads the photo and the spec sheet in one request, with thinking disabled, and writes the "
            "listing as JSON: a title, five bullet points, and a short description. **Write** shows the listing and "
            "saves it.\n\n"
            "Open **Write** to change the instructions or the schema."
        ),
        "write_description": "Writes the listing from the photo and the spec sheet, as JSON, and saves it.",
    },
    "chat-02-summarize-a-voice-note": {
        "input": (
            KEY_STEP + "2. Upload a voice note in **Voice Note**: a recording of up to a few minutes.\n"
            "3. Press **Run**. The transcript and the action items are saved under `text/byteplus`."
        ),
        "transcribe": (
            "Seed 2.0 mini listens to the voice note and writes what is said, word for word, with thinking disabled. "
            "**Transcribe** shows the transcript and saves it."
        ),
        "transcribe_description": "Transcribes the voice note and saves the transcript.",
        "actions": (
            "DeepSeek V4 flash GA continues the same conversation: **conversation** carries the transcript, so the "
            "audio is not sent again. It lists every action item and sums up the note, and **Action Items** saves the "
            "list.\n\n"
            "**Request Options** sends this request at the flex tier, which costs less but can take several minutes."
        ),
        "actions_description": "Lists the action items from the transcript and saves them.",
    },
    "image-01-design-a-character": {
        "input": (
            KEY_STEP + "2. Describe your character in **Character**: who they are, what they wear, and what they "
            "carry.\n"
            "3. Press **Run**. Both images are saved under `image/byteplus`."
        ),
        "design": (
            "Seedream 5.0 flash draws the character in full, from the front, at 3:4. Its **references** carry the "
            "image's own ModelArk address on to **Wave**."
        ),
        "design_description": "Draws the character and saves the image.",
        "wave": (
            "Seedream 5.0 flash edits the character from its address, keeping the outfit, and draws it waving. "
            "Change the prompt in **Wave** to pose the character another way."
        ),
        "wave_description": "Draws the same character waving and saves the image.",
    },
    "image-02-make-a-poster-series": {
        "input": (
            KEY_STEP + '2. Describe the series in **Brief**, starting with how many, such as "Generate 4 posters".\n'
            "3. Press **Run**. Up to four posters are saved under `image/byteplus`."
        ),
        "model": (
            "**Model** holds the model **Series** uses. **Model: Info** shows what the extension knows about it, for "
            "free and without the key, and **Info** shows it as JSON. Seedream 4.0 makes several related images in "
            "one request, so **max images** can be 4. The default, Seedream 5.0 flash, makes one image per request, "
            "so the node refuses 4 for it before sending anything."
        ),
        "series": (
            "Seedream 4.0 draws the posters as one series, so the style and the typeface match. It makes as many as "
            "**Brief** asks for, up to the four **max images** allows."
        ),
        "series_description": "Draws the poster series and saves it.",
    },
    "image-03-split-a-poster-into-layers": {
        "input": (
            KEY_STEP + "2. Describe the poster in **Poster**. Put any words it shows in quotation marks.\n"
            "3. Press **Run**. The poster and each layer are saved under `image/byteplus`."
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
    "video-01-animate-a-character": {
        "input": (
            KEY_STEP + "2. Describe your character in **Character**, and what they do and say in **Scene**. Put "
            "spoken words in double quotation marks.\n"
            "3. Press **Run**. The video is saved under `video/byteplus`."
        ),
        "design": (
            "Seedream 5.0 flash draws the character, which becomes the video's first frame. Seedance refuses "
            "real-looking faces, but trusts the original file of an image Seedream 5.0 drew from a prompt alone, for "
            "30 days; **references** carries that file's address."
        ),
        "design_description": "Draws the character.",
        "animate": (
            "Seedance 2.0 mini starts on the character and makes a five-second 480p video with sound, speaking the "
            "line.\n\n" + RECOVER_STEP
        ),
        "animate_description": "Turns the character into a video and saves it.",
    },
    "video-02-continue-a-shot": {
        "input": (
            KEY_STEP + "2. Describe the first shot in **Opening** and the next in **Next**.\n"
            "3. Press **Run**. Both shots, and the two joined, are saved under `video/byteplus`."
        ),
        "shot_1": (
            "Seedance 2.0 mini makes the first five-second shot at 480p. Its **references** carry the shot's video "
            "and its last frame on, as ModelArk's own files.\n\n" + RECOVER_STEP
        ),
        "shot_1_description": "Makes the first shot and saves it.",
        "shot_2": (
            "The next shot starts on the last frame of the first, so the two cut together. Add more shots the same "
            "way, each connected to the one before.\n\n"
            "To continue the clip itself rather than start from its last frame, use Seedance 2.5, set **omni reference "
            "task type** to **extend**, and connect the first shot's **references** to **references** instead of "
            "**first frame**."
        ),
        "shot_2_description": "Makes the next shot from the first shot's last frame and saves it.",
        "join": "**Concatenate Video** joins the two shots in order, and the result is saved under `video/byteplus`.",
        "join_description": "Joins the two shots and saves the result.",
    },
    "video-03-cast-a-preset-character": {
        "input": (
            KEY_STEP + "2. In the ModelArk console, open **Playground**, choose Seedance 2.5, and open the **Digital "
            "characters** tab. Open a character, copy its asset ID, and paste it into **url** on "
            "**Reference: Add** in **Character**.\n"
            "3. Describe the product in **Product** and the shot in **Scene**.\n"
            "4. Press **Run**. The video is saved under `video/byteplus`."
        ),
        "draw": (
            "Seedream 5.0 flash draws the product. Its **references** carry the image's address on to **Reference: "
            "Add**."
        ),
        "draw_description": "Draws the product.",
        "character": (
            "**Reference: Add** adds the preset character after the product, so the product is Image 1 and the "
            "character Image 2, as **Scene** says. The first run stops here until you paste an asset ID."
        ),
        "film": "Seedance 2.0 mini films the character with the product.\n\n" + RECOVER_STEP,
        "film_description": "Films the preset character with the product and saves the video.",
    },
    "video-04-draft-then-finish": {
        "input": (
            KEY_STEP + "2. Describe the video in **Prompt**.\n"
            "3. Press **Run**. A four-second 480p draft is saved under `video/byteplus`.\n"
            "4. If the draft looks right, select **Finish** and press Ctrl+B to turn it on, then press **Run** again. "
            "Only the finish runs; ComfyUI reuses the draft."
        ),
        "draft": (
            "Seedance 2.5 makes a quick 480p draft. Its **references** carry the draft's task ID, which ModelArk "
            "keeps for seven days."
        ),
        "draft_description": "Makes a four-second 480p draft and saves it.",
        "finish": (
            "**Finish** is off when the workflow opens, because a finished video is billed as a 1080p video. "
            "Seedance 2.5 remakes the draft at 1080p with the same prompt, length, and shape; a draft can be "
            "finished only at 1080p.\n\n"
            "1080p video from Seedance 2.5 is 10-bit H.265. If your player shows nothing, open the file in VLC, mpv, "
            "or QuickTime Player."
        ),
        "finish_description": "Finishes the draft at 1080p and saves it.",
    },
    "video-05-recover-a-video": {
        "recover": (
            "Use this after you cancel a run of **Video: Generate**, after it times out, or after ComfyUI restarts "
            "while a video is being made. ModelArk still makes the video.\n\n"
            + KEY_STEP
            + "2. In **task**, choose the video. Each entry shows its task ID, model, and start time in UTC. Press R "
            "to list tasks started after the page loaded.\n"
            "3. Press **Run**. The video is saved under `video/byteplus`, and **Last Frame** shows its last frame.\n\n"
            "A task leaves the list once its video is saved."
        ),
    },
    "search-01-choose-a-hero-image": {
        "input": (
            KEY_STEP + "2. Describe the product and the picture you need in **Brief**, in one line.\n"
            "3. Press **Run**. The image that best matches the brief is saved under `image/byteplus`."
        ),
        "draw": "Seedream 4.0 draws four options from the brief in one request.",
        "draw_description": "Draws four options from the brief.",
        "score": (
            "Skylark embedding vision turns the brief and each option into an embedding and compares each with the "
            "brief. **Scores** lists the brief first, compared with itself, then each option in order; the highest "
            "after the first is the best match."
        ),
        "score_description": "Embeds the brief and the options, and compares each option with the brief.",
        "choose": (
            "**Choose** picks the best match with ComfyUI's own nodes: **Extract Text** reads each option's score, "
            "**Math Expression** finds the highest with `values.index(max(values))`, and **Get Item From List** takes "
            "that option, which is saved under `image/byteplus`."
        ),
        "choose_description": "Picks the option with the highest score and saves it.",
    },
    "3d-01-turn-a-character-into-a-3d-model": {
        "input": (
            KEY_STEP + "2. Describe your character in **Character**.\n"
            "3. Press **Run**. The 3D model is saved as a GLB file under `3d/byteplus`."
        ),
        "design": (
            "Seedream 5.0 flash draws the character standing in a T-pose, from the front, on a plain white "
            "background, which Hyper3D turns into a clean model."
        ),
        "design_description": "Draws the character in a T-pose.",
        "build": (
            "Hyper3D Gen2 turns the image into a 3D model. Its prompt holds Hyper3D's commands for PBR textures and a "
            "pose ready for rigging: `--material PBR --TAPose true`. **Save 3D Model** saves it and shows it."
        ),
        "recover": (
            "**Recover** is off when the workflow opens. Use it after you cancel a 3D task, or after ComfyUI restarts "
            "while one runs: select **3D: Download** and **Save 3D Model** here, press Ctrl+B to turn them on, choose "
            "the task in **task**, and press **Run**. Press R to list tasks started after the page loaded."
        ),
    },
}

__all__ = ["WORKFLOW_TEXTS"]
