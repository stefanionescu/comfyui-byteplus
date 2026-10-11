# Video: Download

Downloads a video that ModelArk kept making after a run stopped: you
cancelled it, ComfyUI restarted, or it waited too long.

## Inputs

| Input  | What it takes                                                                       |
| ------ | ----------------------------------------------------------------------------------- |
| `task` | A video task started on this server, shown as its ID, model, and start time in UTC. |

## Outputs

| Output       | What it carries                                                                                                    |
| ------------ | ------------------------------------------------------------------------------------------------------------------ |
| `video`      | The video, MP4 or MOV.                                                                                             |
| `last_frame` | The video's last frame, as ModelArk made it. A draft has none.                                                     |
| `references` | The video and its last frame as references valid for 24 hours, or, for a draft, the draft to finish within 7 days. |

## Use

1. Choose the task in `task`. Press R to list tasks started after the page
   loaded.
2. Connect `video` to **Save Video**.
3. Select **Run**.

A task leaves the list once its video is downloaded, or when it fails, is
cancelled, or expires. ModelArk deletes the files 24 hours after the task
finishes. Example: **video-05-recover-a-video**.

[ModelArk video task documentation](https://docs.byteplus.com/en/docs/modelark/get-video-generation-task-api)
