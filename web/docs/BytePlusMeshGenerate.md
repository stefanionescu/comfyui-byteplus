# 3D: Generate

Makes a GLB 3D model with Hyper3D or Hitem3D on BytePlus ModelArk, from a
prompt, images of the subject, or image references.

## Inputs

| Input        | What it takes                                                                                                                                                                                                                                            |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`      | Any 3D model ID from the ModelArk model list, such as `hitem3d-2-0-251223`; the default is `hyper3d-gen2-260112`. Hyper3D works from a prompt, images, or both; Hitem3D from images only.                                                                |
| `images`     | Images of the subject: one, a batch, or a list. Hitem3D reads only addresses; connect references instead.                                                                                                                                                |
| `references` | Image references from **Image: Generate**, **Video: Generate**, or **Reference: Add**.                                                                                                                                                                   |
| `run_number` | Change it to send the same request again.                                                                                                                                                                                                                |
| `options`    | Settings from **Request Options**.                                                                                                                                                                                                                       |
| `prompt`     | What to make, in English, for Hyper3D, then any of the model's own commands, such as `--material PBR --TAPose true`; Hyper3D reads 400 characters in all. The node adds the GLB format command. It can be empty when images or references are connected. |

Before anything is paid, the node refuses a file format command other than
GLB, or no image for Hitem3D.

## Outputs

| Output     | What it carries       |
| ---------- | --------------------- |
| `model_3d` | The 3D model, as GLB. |

## Use

1. Connect images of the subject, or write a prompt.
2. Connect **model_3d** to **Save 3D Model**.
3. Select **Run**.

Example: **3d-01-turn-a-character-into-a-3d-model**.

ModelArk usually starts a task at once, and the task runs to the end and is
billed even if you cancel, ComfyUI restarts, or the request timeout passes;
collect it with **3D: Download**.

[ModelArk 3D generation documentation](https://docs.byteplus.com/en/docs/modelark/shadoweye-create-3d-generation-task-api)
