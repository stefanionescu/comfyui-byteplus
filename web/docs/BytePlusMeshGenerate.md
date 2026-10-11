# 3D: Generate

Makes a GLB 3D model with Hyper3D or Hitem3D on BytePlus ModelArk, from a
prompt, images of the subject, or image references.

## Inputs

| Input        | What it takes                                                                                                                                                                                               |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`      | Any 3D model ID from the ModelArk model list, such as `hitem3d-2-0-251223`; the default is `hyper3d-gen2-260112`. Hyper3D works from a prompt, images, or both; Hitem3D from images only.                   |
| `images`     | Images of the subject: one, a batch, or a list, each under 4096 by 4096 pixels. Hitem3D does not take them; connect references instead.                                                                     |
| `references` | Image references from **Image: Generate**, **Video: Generate**, or **Reference: Add**. Hyper3D takes up to 5 images in all, and Hitem3D up to 4.                                                            |
| `texture`    | `white` makes a plain model, `textured` bakes the lighting into the colors, and `PBR` adds metal, roughness, and normal maps, on Hyper3D only. **model default** is PBR on Hyper3D and textured on Hitem3D. |
| `topology`   | For Hyper3D: `triangles`, or `quads`, which are easier to edit. Quads are the default.                                                                                                                      |
| `faces`      | The number of faces; 0 leaves it to the model. Hyper3D takes 1,000 to 200,000 quads or 500 to 1,000,000 triangles. Hitem3D takes 100,000 to 2,000,000.                                                      |
| `precision`  | For Hitem3D: `standard` or `high`. High costs more.                                                                                                                                                         |
| `pose`       | For Hyper3D: `T or A pose` stands a character in a pose ready for rigging.                                                                                                                                  |
| `views`      | For Hitem3D: the side each image shows, in the order front, back, left, right, such as `front, left`. Connect the images in the same order.                                                                 |
| `run_number` | Change it to send the same request again.                                                                                                                                                                   |
| `options`    | Settings from **Request Options**.                                                                                                                                                                          |
| `prompt`     | What to make, in English, for Hyper3D, which reads 400 characters with the node's settings included. It can be empty when images or references are connected.                                               |

**model default** sends nothing. Before anything is paid, the node refuses a
texture, mesh, face count, precision, pose, views, or number of images the
model does not take, and names what it does take.

## Outputs

| Output     | What it carries       |
| ---------- | --------------------- |
| `model_3d` | The 3D model, as GLB. |

## Use

1. Connect images of the subject, or write a prompt.
2. Connect **model_3d** to **Save 3D Model**.
3. Select **Run**.

Example: **3d-01-turn-a-character-into-a-3d-model**.

ModelArk usually starts a task at once. A task that has started runs to the
end and is billed even if you cancel, ComfyUI restarts, or the request timeout
passes; collect it with **3D: Download**.

[ModelArk 3D generation documentation](https://docs.byteplus.com/en/docs/modelark/shadoweye-create-3d-generation-task-api)
