# Image: Split Layers

Splits one image into a base image and up to 16 transparent layers, such as
each person, object, and block of text, with Seedream 5.0 pro or flash.

## Inputs

| Input                     | What it takes                                                                                                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `model`                   | A Seedream 5.0 pro or flash model ID; the default is `dola-seedream-5-0-flash-260915`.                                                                                         |
| `size`                    | `1K`, `1.5K`, `2K`, or `auto`, which keeps each part near its own size, from 1K to 2K.                                                                                         |
| `optimize_prompt_options` | `standard` or `fast`, sent as `optimize_prompt_options.mode`, on models that offer it.                                                                                         |
| `watermark`               | Adds an AI-generated mark in the lower right corner.                                                                                                                           |
| `image`                   | One image to split, or references that hold one, such as the **references** of **Image: Generate**.                                                                            |
| `run_number`              | Change it to send the same request again.                                                                                                                                      |
| `prompt`                  | What to split out. Leave it empty to split every main part, or mark a region as `<bbox>left top right bottom</bbox>`, from 0 0 at the top left to 999 999 at the bottom right. |
| `options`                 | Settings from **Request Options**.                                                                                                                                             |

ModelArk bills every layer it makes as an image. Name the parts you want in
the prompt to make fewer layers.

## Outputs

| Output   | What it carries                                                                    |
| -------- | ---------------------------------------------------------------------------------- |
| `base`   | The base image the layers sit on.                                                  |
| `layers` | The layers from bottom to top, each placed on a canvas the size of the base image. |
| `masks`  | One mask per layer on the same canvas. White is transparent.                       |

## Use

1. Connect the image and type the model ID.
2. Connect **layers** and **masks** to **Join Image with Alpha**, and its
   image to **Save Image**, to save each layer as a transparent PNG.
3. Select **Run**.

Example: **image-03-split-a-poster-into-layers**.

[ModelArk layer decomposition documentation](https://docs.byteplus.com/en/docs/modelark/seedream-5-0-pro)
