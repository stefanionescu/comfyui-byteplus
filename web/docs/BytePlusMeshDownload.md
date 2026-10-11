# 3D: Download

Downloads a 3D model that ModelArk kept making after a run stopped: you
cancelled it after it started, ComfyUI restarted, or the wait passed the
request timeout.

## Inputs

| Input  | What it takes                                                                    |
| ------ | -------------------------------------------------------------------------------- |
| `task` | A 3D task started on this server, shown as its ID, model, and start time in UTC. |

## Outputs

| Output     | What it carries       |
| ---------- | --------------------- |
| `model_3d` | The 3D model, as GLB. |

## Use

1. Choose the task in **task**. Press R to list tasks started after the page
   loaded.
2. Connect **model_3d** to **Save 3D Model**.
3. Select **Run**.

A task leaves the list once its model is downloaded, or when it failed, was
cancelled, or expired. ModelArk deletes the file 24 hours after the task
finishes. Example: **3d-01-turn-a-character-into-a-3d-model**.

[ModelArk 3D task documentation](https://docs.byteplus.com/en/docs/modelark/shadoweye-get-3d-generation-task-api)
