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
            "Models: Seed 2.0 mini, which reads audio, and DeepSeek V4 flash. Activate them on ModelArk's **Model "
            "activation** page."
        ),
        "transcribe": (
            "Seed 2.0 mini listens to the voice note and writes what is said, word for word, with thinking off. "
            "**Transcribe** shows the transcript and saves it."
        ),
        "transcribe_description": "Transcribes the voice note and saves the transcript.",
        "actions": (
            "DeepSeek V4 flash continues the same conversation: **conversation** carries the transcript, so the "
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
    "video-01-animate-a-character": {
        "input": (
            KEY_STEP + "2. Describe your character in **Character**, and what they do and say in **Scene**. Put "
            "spoken words in double quotation marks.\n"
            "3. Press **Run**. The video is saved under `video/byteplus`.\n\n"
            "Models: Seedream 5.0 flash and Seedance 2.0 mini. Activate them on ModelArk's **Model activation** page."
        ),
        "design": (
            "Seedream 5.0 flash draws the character, which becomes the video's first frame. Seedance refuses images "
            "of real-looking faces, but it trusts images ModelArk made itself for 30 days, as long as it gets the "
            "original file. **references** carries that original address, not a copy."
        ),
        "design_description": "Draws the character.",
        "animate": (
            "Seedance 2.0 mini starts on the character and makes a five-second 480p video with sound, speaking the "
            "line. The character's address works for 24 hours; after that, open **Design** and change **run "
            "number** to draw a new one.\n\n"
            "If you cancel while the task waits in BytePlus's queue, it is cancelled and nothing is billed. Once it "
            "has started, it runs to the end; collect it with **video-05-recover-a-video**."
        ),
        "animate_description": "Turns the character into a video and saves it.",
    },
    "video-02-continue-a-shot": {
        "input": (
            KEY_STEP + "2. Describe the first shot in **Opening** and the next in **Next**.\n"
            "3. Press **Run**. Both shots, and the two joined, are saved under `video/byteplus`.\n\n"
            "Model: Seedance 2.0 mini. Activate it on ModelArk's **Model activation** page."
        ),
        "shot_1": (
            "Seedance 2.0 mini makes the first five-second shot at 480p. Its **references** carry the shot's video "
            "and its last frame on, as BytePlus's own files."
        ),
        "shot_1_description": "Makes the first shot and saves it.",
        "shot_2": (
            "The next shot starts on the last frame of the first, so the two cut together. Add more shots the same "
            "way, each connected to the one before.\n\n"
            "To continue the clip itself rather than start from its last frame, use Seedance 2.5, set **task** to "
            "**extend**, and connect the first shot's **references** to **references** instead of **first frame**."
        ),
        "shot_2_description": "Makes the next shot from the first shot's last frame and saves it.",
        "join": (
            "**Concatenate Video** joins the two shots in order, and the result is saved under `video/byteplus`.\n\n"
            "If you cancel while a shot waits in BytePlus's queue, it is cancelled and nothing is billed. A shot that "
            "has started runs to the end; collect it with **video-05-recover-a-video**."
        ),
        "join_description": "Joins the two shots and saves the result.",
    },
    "video-03-cast-a-preset-character": {
        "input": (
            KEY_STEP + "2. In the ModelArk console, open **Playground**, choose Seedance 2.5, and open the **Digital "
            "characters** tab. Open a character, copy its asset ID, and paste it into **asset ID or address** on "
            "**Reference: Add** in **Character**.\n"
            "3. Describe the product in **Product** and the shot in **Scene**.\n"
            "4. Press **Run**. The video is saved under `video/byteplus`.\n\n"
            "BytePlus allows videos made with preset characters only for trying the models and internal use. Models: "
            "Seedream 5.0 flash and Seedance 2.0 mini. Activate them on ModelArk's **Model activation** page."
        ),
        "product": (
            "Seedream 5.0 flash draws the product. Its **references** carry the image's address on to **Reference: "
            "Add**."
        ),
        "draw_description": "Draws the product.",
        "character": (
            "**Reference: Add** adds the preset character after the product, so the product is Image 1 and the "
            "character Image 2, as **Scene** says. The first run stops here until you paste an asset ID."
        ),
        "video": (
            "Seedance 2.0 mini films the character with the product. BytePlus trusts its preset characters, so their "
            "faces are not blocked.\n\n"
            "If you cancel while the task waits in BytePlus's queue, it is cancelled and nothing is billed. Once it "
            "has started, collect it with **video-05-recover-a-video**."
        ),
        "film_description": "Films the preset character with the product and saves the video.",
    },
    "video-04-draft-then-finish": {
        "input": (
            KEY_STEP + "2. Describe the video in **Prompt**.\n"
            "3. Press **Run**. A four-second 480p draft is saved under `video/byteplus`.\n"
            "4. If the draft looks right, select **Finish** and press Ctrl+B to turn it on, then press **Run** again. "
            "Only the finish runs; ComfyUI reuses the draft.\n\n"
            "Model: Seedance 2.5. Activate it on ModelArk's **Model activation** page."
        ),
        "draft": (
            "Seedance 2.5 makes a quick 480p draft. Its **references** carry the draft's task ID, which BytePlus "
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
            "Use this after you cancel a run of **Video: Generate** once its task has started, after the run times "
            "out, or after ComfyUI restarts while a video is being made. BytePlus keeps making the video. A task that "
            "was still queued when you cancelled was cancelled, and is not listed.\n\n"
            + KEY_STEP
            + "2. In **job**, choose the video. Each entry shows its task ID, model, and start time in UTC. Press R "
            "to list tasks started after the page loaded.\n"
            "3. Press **Run**. The video is saved under `video/byteplus`, and **Last Frame** shows its last frame.\n\n"
            "A task leaves the list once its video is saved. BytePlus deletes a finished video's file after 24 hours."
        ),
    },
    "search-01-choose-a-hero-image": {
        "input": (
            KEY_STEP + "2. Describe the product and the picture you need in **Brief**, in one line.\n"
            "3. Press **Run**. The image that best matches the brief is saved under `image/byteplus`.\n\n"
            "Models: Seedream 4.0 and Skylark embedding vision. Activate them on ModelArk's **Model activation** page."
        ),
        "draw": "Seedream 4.0 draws a series of options from the brief, up to the four **count** allows.",
        "draw_description": "Draws up to four options from the brief.",
        "score": (
            "Skylark embedding vision turns the brief and each option into an embedding, one request per item, and "
            "compares each with the brief. **Scores** lists the brief first, compared with itself, then each option "
            "in order; the highest after the first is the best match."
        ),
        "score_description": "Embeds the brief and the options, and compares each option with the brief.",
        "choose": (
            "**Choose** picks the best match with ComfyUI's own nodes: **Extract Text** reads each option's score, "
            "**Math Expression** finds the highest with `values.index(max(values))`, and **Get Item From List** takes "
            "that option, which is saved under `image/byteplus`. A missing option scores -2, so it is never chosen."
        ),
        "choose_description": "Picks the option with the highest score and saves it.",
    },
    "3d-01-turn-a-character-into-a-3d-model": {
        "input": (
            KEY_STEP + "2. Describe your character in **Character**.\n"
            "3. Press **Run**. The 3D model is saved as a GLB file under `3d/byteplus`.\n\n"
            "BytePlus offers 3D generation only to accounts in some countries. Models: Seedream 5.0 flash and Hyper3D "
            "Gen2. Activate them on ModelArk's **Model activation** page."
        ),
        "design": (
            "Seedream 5.0 flash draws the character standing in a T-pose, from the front, on a plain white "
            "background, which Hyper3D turns into a clean model."
        ),
        "design_description": "Draws the character in a T-pose.",
        "build": (
            "Hyper3D Gen2 turns the image into a 3D model with PBR textures, in a pose ready for rigging. **Save 3D "
            "Model** saves it and shows it.\n\n"
            "If you cancel while the task is queued, it is cancelled and nothing is billed. Once it has started, it "
            "runs to the end; collect it in **Recover**."
        ),
        "recover": (
            "**Recover** is off when the workflow opens. Use it after you cancel a 3D task that had started, or after "
            "ComfyUI restarts while one runs: select **3D: Download** and **Save 3D Model** here, press Ctrl+B to turn "
            "them on, choose the task in **job**, and press **Run**. Press R to list tasks started after the page "
            "loaded."
        ),
    },
}

__all__ = ["WORKFLOW_TEXTS"]
