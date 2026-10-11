# Video: Generate

Makes a video with any Seedance model on BytePlus ModelArk, from a prompt,
first and last frames, reference media, or a draft, and outputs its last frame
and their ModelArk addresses for the next shot.

## Inputs

| Input                      | What it takes                                                                                                                                                                                                                                                        |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                    | Any Seedance model ID from the ModelArk model list; the default is `dreamina-seedance-2-0-mini-260615`.                                                                                                                                                              |
| `duration`                 | The length in seconds. -1 lets the model choose; Seedance 2.5 may then make up to 30 seconds. An `edit` task always sends -1.                                                                                                                                        |
| `resolution`               | `480p`, `720p`, `1080p`, or `4k`; each model takes some of them. A draft is made at 480p, and finishing one sends this value.                                                                                                                                        |
| `ratio`                    | The shape, or `adaptive` to follow the first frame, the edited video, or the prompt.                                                                                                                                                                                 |
| `generate_audio`           | `true` or `false`. **model default** makes sound on models that make it.                                                                                                                                                                                             |
| `omni_reference_task_type` | On Seedance 2.5, `edit` or `extend` edits or extends a reference video, and `reference` follows the references; `auto` lets the model decide.                                                                                                                        |
| `draft`                    | Makes a quick 480p draft, on models that offer drafts. To finish it, connect its **references** to another **Video: Generate** with the same model, an empty prompt, and a **resolution** the model finishes drafts at, such as `1080p` for Seedance 2.5.            |
| `camera_fixed`             | Asks the model to keep the camera still, on models that take it.                                                                                                                                                                                                     |
| `output_format`            | `mp4` or `mov`, on models that offer both.                                                                                                                                                                                                                           |
| `watermark`                | Adds an AI-generated mark in the lower right corner.                                                                                                                                                                                                                 |
| `first_frame`              | One image the video starts from, or references that hold one image. Seedance trusts real-looking faces only in the original files of Seedance 2.x outputs and of images Seedream 5.0 drew from a prompt alone, so connect **references** rather than decoded images. |
| `last_frame`               | One image the video ends on, with a first frame.                                                                                                                                                                                                                     |
| `reference_image`          | Images the video follows: one, a batch, or a list. They are Image 1, Image 2, and so on, before any image references.                                                                                                                                                |
| `reference_audio`          | Audio the video follows: one clip, a batch, or a list.                                                                                                                                                                                                               |
| `references`               | Image, video, and audio references from **Image: Generate**, **Video: Generate**, or **Reference: Add**, or one draft to finish.                                                                                                                                     |
| `seed`                     | Varies the output, on models that take a seed.                                                                                                                                                                                                                       |
| `run_number`               | Change it to send the same request again.                                                                                                                                                                                                                            |
| `prompt`                   | What the video shows. Name media as Image 1, Video 1, and Audio 1. It can be empty when frames or references are connected.                                                                                                                                          |
| `options`                  | Settings from **Request Options**.                                                                                                                                                                                                                                   |

**model default** sends nothing. Before anything is paid, the node refuses a
duration, resolution, ratio, sound, task type, or output format the model does
not take, and names what it does take.

## Outputs

| Output       | What it carries                                                                                                      |
| ------------ | -------------------------------------------------------------------------------------------------------------------- |
| `video`      | The video, MP4 or MOV.                                                                                               |
| `last_frame` | The video's last frame, as ModelArk made it. A draft has none.                                                       |
| `references` | The video and its last frame as references valid for 24 hours, or, after a draft, the draft to finish within 7 days. |

## Use

1. Write the prompt, type the model ID, and connect any frames or references.
2. Connect **video** to **Save Video**.
3. Select **Run**. A video takes from under a minute to several minutes.

Examples: **video-01-animate-a-character**, **video-02-continue-a-shot**, and
**video-04-draft-then-finish**.

ModelArk usually starts a task at once, and the task runs to the end and is
billed even if you cancel, ComfyUI restarts, or the request timeout passes;
collect it with **Video: Download**.

[ModelArk video generation documentation](https://docs.byteplus.com/en/docs/modelark/create-video-generation-task-api)
