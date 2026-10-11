# ![comfyui-byteplus: a ComfyUI extension that runs BytePlus ModelArk models](docs/images/brand/banner.svg)

[![ComfyUI 0.37.2 or later](docs/images/badges/comfyui.svg)](#requirements)
[![Frontend 1.52.7 or later](docs/images/badges/frontend.svg)](#requirements)
[![Python 3.12 or later](docs/images/badges/python.svg)](#requirements)
[![MIT license](docs/images/badges/license.svg)](LICENSE.md)

Run any BytePlus ModelArk model in ComfyUI with your own API key.

## Contents

- [Requirements](#requirements)
- [Install](#install)
- [First run](#first-run)
- [Example workflows](#example-workflows)
- [Nodes](#nodes)
- [Models](#models)
- [How a run works](#how-a-run-works)
- [Development](#development)
- [Common problems](#common-problems)
- [License](#license)

## Requirements

- Python 3.12 or later.
- ComfyUI 0.37.2 or later, with frontend 1.52.7 or later in the 1.x series.
- A ModelArk API key for the Asia Pacific (Johor) region.

Activate each model you plan to use on the **Model activation** page of the
ModelArk console.

## Install

Put the extension in `ComfyUI/custom_nodes/comfyui-byteplus`, install its
`requirements.txt` with ComfyUI's Python, and restart ComfyUI.

### Comfy Desktop

1. In the instance chooser, select the **⋮** icon on the instance card, then
   **Manage**.
2. Under **About**, copy **Location**. In that folder, find the `ComfyUI` folder
   that holds `main.py`, and put the extension in its `custom_nodes` folder.
3. Select **Terminal** in the same panel and run:

```sh
pip install -r custom_nodes/comfyui-byteplus/requirements.txt
```

### macOS or Linux

From the ComfyUI folder:

```sh
.venv/bin/python -m pip install -r custom_nodes/comfyui-byteplus/requirements.txt
```

With uv:

```sh
uv pip install --python .venv/bin/python -r custom_nodes/comfyui-byteplus/requirements.txt
```

### Windows

From the ComfyUI folder, in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\custom_nodes\comfyui-byteplus\requirements.txt
```

### Windows portable

From the folder that holds `ComfyUI` and `python_embeded`, in PowerShell:

```powershell
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\comfyui-byteplus\requirements.txt
```

To update or remove the extension, see the
[advanced guide](ADVANCED.md#update-or-remove).

## First run

1. Save your ModelArk API key in **ComfyUI menu → Extensions → BytePlus →
   BytePlus Settings**.
2. Activate Seedream 5.0 flash (`dola-seedream-5-0-flash-260915`) on the
   **Model activation** page of the ModelArk console.
3. Open **Browse Templates → comfyui-byteplus →
   image-01-design-a-character** and select **Run**.
4. See your character, then the same character waving, in **Design** and
   **Wave**.

To send the same request again, change `run_number`.

## Example workflows

| Workflow                                                                                              | Input                         |
| ----------------------------------------------------------------------------------------------------- | ----------------------------- |
| [Chat: Write a Product Listing](example_workflows/chat-01-write-a-product-listing.json)               | A spec sheet (PDF or text)    |
| [Chat: Summarize a Voice Note](example_workflows/chat-02-summarize-a-voice-note.json)                 | A voice note                  |
| [Image: Design a Character](example_workflows/image-01-design-a-character.json)                       | A character description       |
| [Image: Make a Poster Series](example_workflows/image-02-make-a-poster-series.json)                   | A brief                       |
| [Image: Split a Poster into Layers](example_workflows/image-03-split-a-poster-into-layers.json)       | A poster description          |
| [Video: Animate a Character](example_workflows/video-01-animate-a-character.json)                     | A character and a scene       |
| [Video: Continue a Shot](example_workflows/video-02-continue-a-shot.json)                             | Two shot descriptions         |
| [Video: Cast a Preset Character](example_workflows/video-03-cast-a-preset-character.json)             | A preset character's asset ID |
| [Video: Draft, Then Finish](example_workflows/video-04-draft-then-finish.json)                        | A video description           |
| [Video: Recover a Video](example_workflows/video-05-recover-a-video.json)                             | A video task left running     |
| [Search: Choose a Hero Image](example_workflows/search-01-choose-a-hero-image.json)                   | A brief                       |
| [3D: Turn a Character into a 3D Model](example_workflows/3d-01-turn-a-character-into-a-3d-model.json) | A character description       |

They are in **Browse Templates → comfyui-byteplus**. Start with each
workflow's **Start Here** note. Most steps are subgraphs. Media inputs start
empty, and most workflows draw their own inputs with Seedream.

![Screenshot of video-01: the Start Here note and a note for each step sit above three groups. Input holds the Character and Scene prompts, Portrait holds the Portrait subgraph, which draws the character, and Animate holds the Animate subgraph, which starts the video on that character.](docs/images/screenshots/video-01-workflow.png)

After an update, open the examples in a new tab to get the new versions.

## Nodes

The nodes are under **BytePlus** in the node menu, and each has a help page.

![Node map: one card for each kind of node. Chat: Attach Document feeds Chat: Ask, and Image: Generate feeds Image: Split Layers. Reference: Add adds files to the references of the chat, image, video, and 3D nodes. Video: Download and 3D: Download collect tasks left running. Request Options and Model: Info are shared. A blue square marks a node that sends a paid request, and a hollow square one that bills nothing.](docs/images/diagrams/node-map.svg)

| Node                                                            | What it does                                                                                | Paid |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ---- |
| [Chat: Ask](web/docs/BytePlusChatAsk.md)                        | Asks a model a question, with images, video, audio, or documents, and returns text or JSON. | Yes  |
| [Chat: Attach Document](web/docs/BytePlusChatAttachDocument.md) | Attaches a PDF or text file from ComfyUI's input folder.                                    | No   |
| [Image: Generate](web/docs/BytePlusImageGenerate.md)            | Generates or edits images with Seedream, and outputs their addresses as references.         | Yes  |
| [Image: Split Layers](web/docs/BytePlusImageSplitLayers.md)     | Splits an image into a base image and transparent layers.                                   | Yes  |
| [Video: Generate](web/docs/BytePlusVideoGenerate.md)            | Makes or extends a video with Seedance, from a prompt, frames, references, or a draft.      | Yes  |
| [Video: Download](web/docs/BytePlusVideoDownload.md)            | Downloads a video that ModelArk kept making after a run stopped.                            | No   |
| [Reference: Add](web/docs/BytePlusReferenceAdd.md)              | Adds a preset character, an asset, or a public file address to a chain of references.       | No   |
| [Search: Embed](web/docs/BytePlusSearchEmbed.md)                | Turns text, images, and videos into embeddings and compares them.                           | Yes  |
| [3D: Generate](web/docs/BytePlusMeshGenerate.md)                | Makes a GLB 3D model from a prompt or images.                                               | Yes  |
| [3D: Download](web/docs/BytePlusMeshDownload.md)                | Downloads a 3D model that ModelArk kept making after a run stopped.                         | No   |
| [Request Options](web/docs/BytePlusRequestOptions.md)           | Sets the flex service tier and extra request fields for paid nodes.                         | No   |
| [Model: Info](web/docs/BytePlusModelInfo.md)                    | Shows what a model reads, makes, and takes, as JSON.                                        | No   |

## Models

Each paid node takes any model ID from the
[ModelArk model list](https://docs.byteplus.com/en/docs/modelark/model-list),
including newer versions of the models the extension knows. **Model: Info**
shows what a known model takes, for free and without a key.

![Video: Generate on the canvas: sockets for first_frame, last_frame, reference_image, reference_audio, references, and options; model set to dreamina-seedance-2-0-mini-260615; duration 5, resolution 720p, ratio, generate_audio, omni_reference_task_type, draft, camera_fixed, output_format, watermark, seed, and run_number; and a prompt about a red fox in the snow.](docs/images/screenshots/video-generate-node.png)

Before sending, the node checks your request against the extension's own
table of ModelArk models, and stops before anything is paid if the model
cannot take it. The error names what the model does take. The
[advanced guide](ADVANCED.md#models) lists every check and each node's default
model.

## How a run works

1. The node checks its inputs against the model's row in the extension's
   table, and stops before anything is paid.
2. It sends the request with your key, straight to ModelArk. Nothing is sent
   twice. A video or 3D task is recorded, checked until ready, and
   downloaded.
3. Outputs also carry the ModelArk address of each file, so the next node
   sends that address instead of uploading the file again. Nodes connected to
   an empty output are skipped.

The [advanced guide](ADVANCED.md#what-each-node-sends) lists what each node
sends and returns.

## Development

Development needs mise. Point the checks at ComfyUI in `.mise.local.toml`:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

Install the tools, dependencies, and Git hooks, and run the full check:

```shell
mise trust
mise run repo:setup
mise run repo:check
```

Restart ComfyUI after changing Python. After changing the browser code, run
`mise run comfy:frontend:build`; after changing a workflow description, run
`mise run comfy:workflows:build`. The [advanced guide](ADVANCED.md#development)
lists every task.

## Common problems

| Problem                                    | Fix                                                                                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| No BytePlus nodes in the menu              | Check that the folder is `ComfyUI/custom_nodes/comfyui-byteplus`, ComfyUI is 0.37.2 or later, and the console shows no import error. |
| No **BytePlus** entry under **Extensions** | Check that `web/extension.js` exists in the extension's folder, then reload the window.                                              |
| The settings cannot be changed             | ComfyUI runs in multi-user mode or is open from another computer. Set `ARK_API_KEY` where ComfyUI starts instead.                    |
| `pydantic` cannot be imported              | Install `requirements.txt` with the Python that runs ComfyUI, then restart.                                                          |
| Node help is missing                       | Reinstall the whole extension, including `web/docs`.                                                                                 |
| The templates are missing                  | Reinstall the whole extension, including `example_workflows`.                                                                        |
| Nodes or menus appear twice                | Keep one `comfyui-byteplus` folder in `custom_nodes`; move copies elsewhere.                                                         |

More in the [advanced guide's troubleshooting](ADVANCED.md#troubleshooting).

## License

[MIT](LICENSE.md).
