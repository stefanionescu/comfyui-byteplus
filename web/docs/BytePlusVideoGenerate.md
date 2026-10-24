# Video: Generate

Makes a video with any Seedance model on BytePlus ModelArk, from a prompt,
first and last frames, reference media, or a draft. It outputs the video, its
last frame, and their ModelArk addresses for the next shot.

## Inputs

| Input                      | What it takes                                                                                                                                                                                                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                    | Any Seedance model ID from the ModelArk model list; the default is `dreamina-seedance-2-0-mini-260615`.                                                                                                                                                           |
| `duration`                 | The length in seconds. -1 lets the model choose, and Seedance 2.5 can then make up to 30 seconds. An `edit` task always sends -1.                                                                                                                                 |
| `resolution`               | `480p`, `720p`, `1080p`, or `4k`; each model takes some of them. A draft is made at 480p, and finishing one sends this value.                                                                                                                                     |
| `ratio`                    | The shape, or `adaptive` to follow `first_frame`, the edited video, or the prompt.                                                                                                                                                                                |
| `generate_audio`           | `true` or `false`. `default` makes sound on models that make it.                                                                                                                                                                                                  |
| `omni_reference_task_type` | On Seedance 2.5, `edit` or `extend` edits or extends a reference video, and `reference` follows the references; `auto` lets the model decide.                                                                                                                     |
| `draft`                    | Makes a quick 480p draft, on models that offer drafts. To finish it, connect its `references` to another **Video: Generate** with the same model and an empty prompt. Set its `resolution` to one the model finishes drafts at, such as `1080p` for Seedance 2.5. |
| `camera_fixed`             | Asks the model to keep the camera still, on models that take it.                                                                                                                                                                                                  |
| `output_format`            | `mp4` or `mov`, on models that offer both.                                                                                                                                                                                                                        |
| `watermark`                | Adds an AI-generated mark in the lower right corner.                                                                                                                                                                                                              |
| `first_frame`              | One image the video starts from, or references that hold one image. To keep a real-looking face that Seedream 5.0 or Seedance made, connect `references`, not a decoded image.                                                                                    |
| `last_frame`               | One image the video ends on, with `first_frame`.                                                                                                                                                                                                                  |
| `reference_image`          | Images the video follows: one, a batch, or a list. They are Image 1, Image 2, and so on, before any image references.                                                                                                                                             |
| `reference_audio`          | Audio the video follows: one clip, a batch, or a list.                                                                                                                                                                                                            |
| `references`               | Image, video, and audio references from **Image: Generate**, **Video: Generate**, or **Reference: Add**, or one draft to finish.                                                                                                                                  |
| `seed`                     | Varies the output, on models that take a seed.                                                                                                                                                                                                                    |
| `run_number`               | Change it to send the same request again.                                                                                                                                                                                                                         |
| `prompt`                   | What the video shows. Name media as Image 1, Video 1, and Audio 1. It can be empty when frames or references are connected.                                                                                                                                       |
| `options`                  | Settings from **Request Options**.                                                                                                                                                                                                                                |

`default` sends nothing. Before you pay anything, the node refuses a
`duration`, `resolution`, `ratio`, `generate_audio`, `omni_reference_task_type`,
or `output_format` the model does not take, and names what it does take.

## Outputs

| Output       | What it carries                                                                                                      |
| ------------ | -------------------------------------------------------------------------------------------------------------------- |
| `video`      | The video, MP4 or MOV.                                                                                               |
| `last_frame` | The video's last frame, as ModelArk made it. A draft has none.                                                       |
| `references` | The video and its last frame as references valid for 24 hours, or, after a draft, the draft to finish within 7 days. |

## Use

1. Write the prompt, type the model ID, and connect any frames or references.
2. Connect `video` to **Save Video**.
3. Select **Run**. A video takes from under a minute to several minutes.

Examples: **video-01-animate-a-character**, **video-02-continue-a-shot**, and
**video-04-draft-then-finish**.

ModelArk starts most tasks at once. A started task runs to the end, and
ModelArk bills it even if you cancel, ComfyUI restarts, or the request timeout
in **BytePlus Settings** passes. Collect it with **Video: Download**.

[ModelArk video generation documentation](https://docs.byteplus.com/en/docs/modelark/create-video-generation-task-api)
