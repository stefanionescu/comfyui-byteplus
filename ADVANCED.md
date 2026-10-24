# ComfyUI BytePlus Advanced Guide

## Contents

- [What each node sends](#what-each-node-sends)
- [Keys and access](#keys-and-access)
- [Settings](#settings)
- [Models](#models)
- [Characters and references](#characters-and-references)
- [Caching and reruns](#caching-and-reruns)
- [Recover a video or 3D task](#recover-a-video-or-3d-task)
- [Limits](#limits)
- [When a node stops](#when-a-node-stops)
- [Use from another extension](#use-from-another-extension)
- [Update or remove](#update-or-remove)
- [Development](#development)
- [Package and publish](#package-and-publish)
- [Troubleshooting](#troubleshooting)

## What each node sends

**Chat: Ask** sends, in this order, the documents, the images as PNG, image
references, the videos as MP4, video references, the audio as WAV, and audio
references, then the prompt. PDF files go as files and text files as text.
Earlier turns come from `conversation`. It returns the answer, the reasoning
when the model shares it, and the conversation.

**Image: Generate** sends the prompt, the chosen settings, each image in
`image` as PNG, and image references as their addresses. When `max_images` is
above 1, it asks for sequential image generation of up to that many images. It
returns the images, their masks, and their addresses as references. White is
transparent in a mask.

**Image: Split Layers** sends one image or image reference. It returns the base
image, each layer, and the mask of each layer.

**Video: Generate** sends the prompt, the length, the resolution, the chosen
settings, the frames, `reference_image`, `reference_audio`, and `references`.
It records the task as soon as ModelArk accepts it, checks it every 10
seconds, and downloads the video and its last frame when it is ready.

**Video: Download** checks one recorded task and downloads its video. Status
checks and downloads are free.

**Reference: Add** adds an asset ID or a public address to a chain of
references. It sends nothing.

**Search: Embed** sends each text line, image, and video in its own request,
one after another. It compares each embedding with the first one locally.

**3D: Generate** sends the prompt with the model's own commands and the GLB
format command, the images as PNG, and the image references, as one task. It
records the task, checks it every 10 seconds, and downloads the GLB file.

**3D: Download** collects a recorded 3D task.

**Request Options** adds `service_tier` and `extra_fields` to the request of
each connected paid node.

**Model: Info** reads the model table bundled with the extension and returns
one row as JSON. It sends nothing.

Every request goes out once. The extension downloads the files ModelArk makes
without the key.

## Keys and access

In the ComfyUI menu, select **Extensions**, then **BytePlus**, then **BytePlus
Settings**, and save the key. The extension stores the key in the private
folder, and the first request that uses the key checks it. `ARK_API_KEY`, set
where ComfyUI starts, takes precedence.

You can change the key and settings only over a direct local connection to the
ComfyUI server. For remote access, a reverse proxy, or multi-user mode, set
`ARK_API_KEY` instead.

The private folder is:

| System  | Folder                                             |
| ------- | -------------------------------------------------- |
| macOS   | `~/Library/Application Support/BytePlusComfyUI`    |
| Linux   | `${XDG_STATE_HOME:-~/.local/state}/byteplus-comfy` |
| Windows | `%LOCALAPPDATA%\BytePlusComfyUI`                   |

To use another folder, set `BYTEPLUS_COMFY_STATE_DIRECTORY` to an absolute
path outside the extension and ComfyUI's folders. The extension does not
encrypt these files, and only their owner can open them.

## Settings

Change these in **BytePlus Settings**. New requests use the saved values.

![The BytePlus Settings dialog: Credentials with the ModelArk API key field, Save Key, and Clear Saved Key, and Request limits with fields for the request timeout in seconds, the maximum upload size in MB, and the maximum download size in MB, and Save Limits.](docs/images/screenshots/settings-dialog.png)

| Setting                        | Default | Range      | What it limits                                                         |
| ------------------------------ | ------- | ---------- | ---------------------------------------------------------------------- |
| **Request timeout (seconds)**  | 1800    | 10 to 3600 | How long one request may take; for a video or 3D task, the whole wait. |
| **Maximum upload size (MB)**   | 64      | 1 to 64    | The media and documents in one request.                                |
| **Maximum download size (MB)** | 512     | 16 to 4096 | The largest reply, image, video, or 3D file accepted.                  |

## Models

The extension bundles a table of every model it knows: what each model reads,
and the settings and limits it takes. ModelArk's model list does not give these
for image, video, or 3D models. Before it sends, a paid node finds its model in
the table. It stops before you pay anything when:

- the ID is empty, is an endpoint ID (`ep-…`), belongs to no family in the
  table, or names a family without its six-digit version;
- the model belongs to another node, such as a video model in
  **Image: Generate**;
- connected images, video, audio, or PDFs are media the model does not read;
- a setting is one the model does not take, or a value outside what it takes;
- **Request Options** sets `service_tier` to `flex` on a model that does not
  take it.

The message names what the model takes. A paid node checks a newer version of
a known model, such as a future `seed-2-0-lite-261201`, against the newest row
of its family, and sends the ID as typed. **Model: Info** returns the row a
node uses, as JSON, and bills nothing.

**Chat: Ask** also takes a chat model newer than the table. The node reads
ModelArk's model list once per ComfyUI session and checks the media against
what the list says the model reads. Such a model takes no `thinking`,
`reasoning_effort`, or PDFs, and it takes every sampling setting and up to
four `stop` words.

| Node                | Default model                       |
| ------------------- | ----------------------------------- |
| Chat: Ask           | `seed-2-0-lite-260428`              |
| Image: Generate     | `dola-seedream-5-0-flash-260915`    |
| Image: Split Layers | `dola-seedream-5-0-flash-260915`    |
| Video: Generate     | `dreamina-seedance-2-0-mini-260615` |
| Search: Embed       | `skylark-embedding-vision-251215`   |
| 3D: Generate        | `hyper3d-gen2-260112`               |

## Characters and references

The Seedance 2.0 and 2.5 models refuse reference images and videos with
real-looking faces. They accept these characters:

- A preset character from ModelArk's digital character library, added with
  **Reference: Add**.
- An image Seedream 5.0 drew from a prompt alone, or a video or its last
  frame from these Seedance models, made with your account in the last 30
  days. Seedance trusts only the original file, so connect the `references`
  output, not the decoded image.
- An asset from your ModelArk asset library, added by its ID with
  **Reference: Add**.

A reference is a file address that ModelArk downloads itself:

- an output address from **Image: Generate**, **Video: Generate**, or
  **Video: Download**;
- an asset, such as `asset://asset-…`;
- a public `https://` address added with **Reference: Add**.

**Video: Generate** numbers media by kind, in the order it sends them: Image
1, Image 2, Video 1, Audio 1. Images connected to `reference_image` come
first, then image references in chain order. Audio works the same way, and
videos come only from references. **Reference: Add** puts its reference after
the ones it receives. Name each file in the prompt by its place. For example,
"the person in Image 2" names a person in the second image.

| Reference                                        | Lasts                                 |
| ------------------------------------------------ | ------------------------------------- |
| Output address of an image, video, or last frame | 24 hours                              |
| Draft                                            | 7 days                                |
| Asset                                            | Until it is deleted from your library |

ModelArk takes a reference video only as a public address or an asset. To edit
or extend your own video, put it at a public address and add it with
**Reference: Add** as a video.

## Caching and reruns

- Change `run_number` to send the same request again.
- The `seed` of **Video: Generate** starts at `fixed`. Set **control after
  generate** to `randomize` to send a new request each run.
- Saving a different key invalidates the cached results; changing settings
  does not.
- The extension sends every request once.
- Cancelling stops the wait. A chat model still bills the tokens it produced,
  and a video or 3D task that has started keeps running.

## Recover a video or 3D task

**Video: Generate** and **3D: Generate** record each task as soon as ModelArk
accepts it. ModelArk starts most tasks at once. A started task runs to the
end, and ModelArk bills it even if you cancel, ComfyUI restarts, or the
request timeout in **BytePlus Settings** passes. Collect it with
**Video: Download** or **3D: Download**, and press R to list new tasks. A task
leaves the list once a node downloads its file, or when its status becomes
`failed`, `cancelled`, or `expired`.

## Limits

The extension adds no limits of its own to what a request holds. Only your
settings and the model's limits apply: the **Request limits** in **BytePlus
Settings**, and the limits **Model: Info** reports. ModelArk refuses a request
outside the model's limits.

## When a node stops

Paid nodes check these before sending, along with the [model checks](#models).
Every paid node stops when:

- Its media are over the upload limit.
- A reference has expired, or is a kind the node does not take. Only
  **Video: Generate** takes assets and drafts, and never as a frame.
- An input other than its media receives a list of several values.

**Chat: Ask** stops when the prompt is empty, or `json_schema` is not a JSON
object.

**Chat: Attach Document** stops when:

- You chose no file, or the file is outside the input folder.
- The file is not a PDF or text file, is over the upload limit, or is not UTF-8
  text.

**Image: Generate** stops when the prompt is empty, or a transparent background
asks for JPEG or lacks exactly one reference image with transparency.

**Image: Split Layers** stops when `image` holds no image or more than one.

**Video: Generate** stops when:

- It gets no prompt, frame, or reference media.
- You connect `last_frame` without `first_frame`.
- Frames and reference media are both connected, or a frame holds more than one
  image.
- The prompt holds a setting that an input of the node sets, such as
  `--duration 5`.
- `omni_reference_task_type` is `edit` or `extend` without a reference
  video, or `reference` without reference media.
- A draft to finish comes with a prompt, other media, or `draft` turned on.

**Reference: Add** stops when `url` is empty, is not an asset ID, an
`asset://` address, or an `https://` address, or is already in the chain.

**Search: Embed** stops when there are no items, or a line, image, or video is
outside the sizes ModelArk embeds.

**3D: Generate** stops when:

- It gets no prompt and no image.
- Hitem3D gets no image.
- The prompt is longer than Hyper3D reads, or asks for a file format other
  than GLB.

**Video: Download** and **3D: Download** stop when the chosen task is not
recorded on this server.

**Request Options** stops when `extra_fields` is not a JSON object. A paid
node stops when the options set a field the node sets itself.

**Model: Info** stops on the IDs the [model checks](#models) refuse.

## Use from another extension

Another extension can call these nodes instead of copying their choices or a
model's limits:

```python
clone = nodes.NODE_CLASS_MAPPINGS["BytePlusModelInfo"].PREPARE_CLASS_CLONE(None)
clone.hidden = io.HiddenHolder.from_dict({})
output = clone.execute(model="dreamina-seedance-2-0-mini-260615")
row = json.loads(output.args[0])
```

- Call a node by its ID on a class clone with an empty hidden holder, as above.
  A called node leaves the progress bar of the calling node alone.
- **Model: Info**, **Reference: Add**, and **Request Options** return at once,
  as above; await every other node.
- A node that takes input lists, such as **Chat: Ask**, takes every input as a
  one-item list; only its media inputs hold several items.
- Read the choices of a dropdown from the schema of the node, such as
  `/object_info/BytePlusVideoGenerate`, instead of copying them.
- Read a model's limits with **Model: Info**.
- A failed request raises an error whose `code` names its kind, such as
  `rate_limited`, `timeout`, or `uncertain`. Check `code`, not the message
  text, which can change.
- Do not send a failed paid request again: it may have run, and ModelArk may
  have billed it.

## Update or remove

To update, replace the `custom_nodes/comfyui-byteplus` folder, install its
`requirements.txt` with ComfyUI's Python, and restart. Open the updated
examples in a new tab.

To remove it, move the folder out of `custom_nodes` and restart. The
[private folder](#keys-and-access) stays; delete it to remove the saved key,
settings, and task records.

## Development

### Setup

Name your ComfyUI install in `.mise.local.toml`, which Git ignores:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

Then install the tools, the dependencies, and the Git hooks:

```shell
mise trust && mise run setup
```

`mise run setup` runs `mise install`, then `mise run deps`, then
`bun run gspot install`:

- `mise run deps` installs the locked Python and Bun dependencies. It also
  writes a path file that shows the type checker the ComfyUI install.
- `bun run gspot install` installs the gspot tools and the Git hooks.

### Checks

gspot runs every check. From the repository folder:

```shell
bun run --no-install gspot check           # Check the working tree
bun run --no-install gspot check --fix     # Run the fixers, then check
bun run --no-install gspot check --staged  # Check what you staged
```

To learn what a check looks for, run `bun run --no-install gspot explain`
with the name of the check. The checks cover:

- Formatting: Ruff, Prettier, taplo, and shfmt.
- Linting: Ruff, ESLint, stylelint, ShellCheck, markdownlint, Vale, and typos.
- Types: basedpyright in strict mode against the ComfyUI install, and `tsc`.
- Dependencies and secrets: deptry, knip, osv-scanner, and Gitleaks.
- Licenses and links.
- Structure: naming, import rules, duplication, and function size.

The settings are in `gspot.toml`. From it, `bun run --no-install gspot apply`
writes `ruff.toml`, `eslint.config.mjs`, `prettier.config.mjs`,
`pyrightconfig.json`, `.stylelintrc.json`, `.markdownlint.jsonc`,
`.editorconfig`, `.prettierignore`, and the `.gspot/` folder. Change
`gspot.toml`, not these files.

### Project checks

The `[[command_check]]` records in `gspot.toml` add the checks of this
project, and gspot runs them with the others:

| Check               | Stage  | What it checks                                                                                                                                                                              |
| ------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `comfy-boundary`    | commit | import-linter checks that only `src/comfy`, `src/nodes`, and the package entry import the modules of ComfyUI. The contract is in `pyproject.toml`.                                          |
| `frontend-bundle`   | commit | `web/extension.js` and `web/extension.css` match their source.                                                                                                                              |
| `requirements`      | commit | `requirements.txt` lists the runtime dependencies of `pyproject.toml`.                                                                                                                      |
| `node-schemas`      | push   | The `send` parameters of each paid node, or the `execute` parameters of each other node, match its inputs. Every node has a help page that names real sockets, and sits in a BytePlus menu. |
| `example-workflows` | push   | The example workflows and the subgraph blueprints match their descriptions. The README links each workflow, and every node appears in a workflow.                                           |

`mise run comfy:frontend:check`, `mise run comfy:nodes:check`, and
`mise run comfy:workflows:check` run the browser-file, node, and workflow
checks alone.

### Generated files

```shell
mise run comfy:requirements:build  # Write requirements.txt from pyproject.toml
mise run comfy:frontend:build      # Build the browser files
mise run comfy:workflows:build     # Build the example workflows
```

The workflow build writes the example workflows from
`scripts/workflows/descriptions/`: one module per category, the group notes in
`notes.py`, and the titles in `texts.py`. The build reads the node definitions
through ComfyUI's Python. It also writes every subgraph to `subgraphs/`, which
ComfyUI lists under **Subgraph Blueprints** in its node library.

### Git hooks

`bun run gspot install` points `core.hooksPath` at `.gspot/hooks`:

- **pre-commit** runs the commit checks on the staged files.
- **commit-msg** checks the [conventional
  commit](https://www.conventionalcommits.org/) format, `type(scope): subject`.
  The scopes are `nodes`, `frontend`, `workflows`, `docs`, `hooks`, `quality`,
  `root`, and `deps`.
- **pre-push** checks each pushed commit with the commit and push checks.

### Test a change

Testing is manual: restart ComfyUI after Python changes, or rebuild the
browser files and reload after browser changes, then run the affected
workflows with inexpensive models.

### Import rules

The `[[import_rule]]` records in `gspot.toml` list what each package imports
besides itself:

| Package                             | Imports                                        |
| ----------------------------------- | ---------------------------------------------- |
| `src/config`                        | Nothing                                        |
| `src/state`                         | config                                         |
| `src/storage`                       | config and state                               |
| `src/byteplus` and `src/settings`   | config, state, and storage, and not each other |
| `src/comfy`                         | config, state, storage, byteplus, and settings |
| `src/nodes`                         | config, state, byteplus, and comfy             |
| `__init__.py` and `src/__init__.py` | comfy and nodes                                |
| `scripts/`                          | config, comfy, and nodes                       |

In the browser code, the page modules import only each other,
`web/scripts/settings/` imports the page modules, and
`web/scripts/extension.ts` imports both.

- Only `src/comfy/`, `src/nodes/`, and the package entry import the modules of
  ComfyUI. The `comfy-boundary` check enforces this rule.
- `src/state/` holds the records.
- All BytePlus requests are in `src/byteplus/`.
  `src/byteplus/transport.py` is the one place that sends the API key.
- The model table, every message, and every other fixed value, such as a
  limit, a step, a file name, or a route, are constants in `src/config/`.
  The dialog text is in `web/scripts/text.ts`.
- Node names, descriptions, and tooltips are in the `io.Schema` call of each
  node.

### Names

Names follow `.gspot/configurations/general/naming/rules/NAMING.md`. The
naming checks refuse banned words, wrong cases, digits, and names of more than
four words.

### Images

The README and this guide use these images:

- `docs/images/brand/banner.svg`, `docs/images/diagrams/node-map.svg`, and the
  four SVG files in `docs/images/badges/` are SVG files; edit them as text.
  They use black `#06080D`, surfaces `#10141B`, hairlines `#232A35`, light text
  `#EEF3FF`, muted text `#8A93A3`, accent `#5C9DFF`, and the blue gradient
  `#9CC4FF` to `#2F80FF`. Headings use Helvetica Neue with tight spacing;
  labels use a monospace font in wide-spaced capitals.
- `docs/images/brand/logo.png` is the mark of the extension: a rounded node
  tile in BytePlus blue `#0066FC` with a cut-out plus and an output socket on
  its right edge. It is 400 × 400 pixels, on a transparent background.
- The banner draws the same mark, and `pyproject.toml` names the logo as the
  Registry icon.
- The node map has one card for each kind of node. A blue square marks a node
  that sends a paid request and a hollow square one that bills nothing. A blue
  arrow runs from an output to the input it feeds.
- The badges under the banner name the ComfyUI, frontend, and Python versions
  and the license, as black pills with a blue value; update them when those
  change.
- `docs/images/screenshots/video-01-workflow.png` is video-01 at 100% zoom,
  with link midpoint markers off.
- `docs/images/screenshots/video-generate-node.png` is a new
  **Video: Generate** node, 420 pixels wide, at 100% zoom, with a prompt typed
  in.
- `docs/images/screenshots/settings-dialog.png` is the **BytePlus Settings**
  dialog with default settings and a saved key.

Keep each image under 100 KB, and give it alt text.

### Change text

- **A message:** edit its constant in `src/config/messages/`, and its entry
  under [troubleshooting](#troubleshooting) if it has one.
- **The labels or tooltips of a node:** edit its `io.Schema` call in
  `src/nodes/`, then its help page in `web/docs/`.
- **The dialogs:** edit `web/scripts/text.ts`, then rebuild the browser files.
- **A workflow's notes:** edit `scripts/workflows/descriptions/notes.py`; for
  titles, `texts.py`; for nodes, models, or prompts, the workflow's module. Then
  rebuild the workflows.
- **The model table:** edit the model's row in `src/config/models/`, then the
  help page of the node if the families change.
- **The default model of a node:** edit `src/config/generation/models.py`, then
  the table under [models](#models) and the help page of the node.

## Package and publish

[comfy-cli](https://github.com/Comfy-Org/comfy-cli) builds and publishes the
Comfy Registry package. These steps use version 1.20.0.

1. Create a publisher and a publishing key in the
   [Comfy Registry](https://docs.comfy.org/registry/publishing).
2. In `pyproject.toml`, set `[tool.comfy].PublisherId` to your publisher ID, add
   `Repository` under `[project.urls]`, and set `[project].version`. Use a new
   version number for each release.
3. Rebuild the generated files:

    ```sh
    mise run comfy:requirements:build
    mise run comfy:frontend:build
    mise run comfy:workflows:build
    ```

4. Commit everything. The packer takes only files Git tracks, and
   `.comfyignore` leaves out development files.
5. Build and check the package:

    ```sh
    mise run comfy:release:package
    ```

    This runs `bun run --no-install gspot check`, packs `node.zip` with
    `comfy node pack`, lists its contents, and scans it with Gitleaks.

6. Publish:

    ```sh
    mise run comfy:release:publish
    ```

    This runs the package steps, then `comfy node publish`, which asks for the
    publishing key.

7. Install the published version with ComfyUI Manager, and check that the nodes,
   menus, help pages, and templates load.

Publishing rebuilds the archive from the checkout, so publish the same commit
you packaged.

## Troubleshooting

Most messages say what to do. These need more.

### Set your ModelArk API key in BytePlus Settings

Save the key in **BytePlus Settings**, or set `ARK_API_KEY` where ComfyUI
starts and restart.

### ModelArk did not accept the API key

`ARK_API_KEY` takes precedence over the saved key; check both.

### This model is not activated on your BytePlus account

Activate it on the **Model activation** page of the ModelArk console.

### ModelArk refused a reference that may show a real person

See [characters and references](#characters-and-references) for the
characters Seedance accepts.

### ModelArk's content check refused an input

A failed generation is not billed.

### ModelArk is limiting requests from your account

Wait a minute and run again, or run fewer paid nodes at once. The extension
does not send the request again for you.

### You cannot change that BytePlus setting here

Reload the window.

### BytePlus's settings file has an unknown setting

Delete the settings file in the [private folder](#keys-and-access) to return
to the defaults.

### A BytePlus state file is larger than expected

Delete it; a task record can go once you have its file.
