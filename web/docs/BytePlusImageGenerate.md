# Image: Generate

Generates or edits images with any Seedream model on BytePlus ModelArk, and
outputs each image's ModelArk address as a reference.

## Inputs

| Input                     | What it takes                                                                                                                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                   | Any Seedream model ID from the ModelArk model list; the default is `dola-seedream-5-0-flash-260915`.                                                                                        |
| `size`                    | A size such as `2K`, or pixels such as `2048x1152`. Each model takes some sizes by name; **Model: Info** lists them. Empty leaves it to the model.                                          |
| `max_images`              | The most images to make, 1 to 15. Above 1, only models with sequential image generation take it. Ask for that many in the prompt, such as "Generate 4 images of …", or the model makes one. |
| `background`              | `transparent` keeps the transparency of one reference image that has it, such as one from **Join Image with Alpha**, and makes a PNG.                                                       |
| `output_format`           | `png` or `jpeg`. `default` makes JPEG. Seedream 4.5 and 4.0 always make JPEG.                                                                                                               |
| `optimize_prompt_options` | `standard` or `fast`, sent as `optimize_prompt_options.mode`. `fast` makes images sooner at slightly lower quality, on models that offer it.                                                |
| `watermark`               | Adds an AI-generated mark in the lower right corner.                                                                                                                                        |
| `image`                   | Images to edit or combine: one, a batch, or a list, each at its own size. They are Image 1, Image 2, and so on, before any `references`.                                                    |
| `references`              | Image references from **Image: Generate**, **Video: Generate**, or **Reference: Add**. Assets are refused.                                                                                  |
| `run_number`              | Change it to send the same request again.                                                                                                                                                   |
| `prompt`                  | What to draw or change. Name each image by its place, such as Image 1 or Image 2.                                                                                                           |
| `options`                 | Settings from **Request Options**.                                                                                                                                                          |

`default` sends nothing. Before you pay anything, the node refuses a
`size`, `max_images`, `background`, or `output_format` the model does not
take, naming what it does take.

## Outputs

| Output       | What it carries                                                                                |
| ------------ | ---------------------------------------------------------------------------------------------- |
| `images`     | The images, each at its own size.                                                              |
| `masks`      | One mask per image, from its transparency. White is transparent; opaque images are all black.  |
| `references` | Each image's ModelArk address, valid for 24 hours, so another node can send the original file. |

## Use

1. Write the prompt and type the model ID.
2. Connect any images to `image`, or references to `references`.
3. Connect `images` to **Save Image**, and select **Run**. To start a video
   from an image, connect `references` to `first_frame` on **Video:
   Generate**.

Examples: **image-01-design-a-character** and
**image-02-make-a-poster-series**.

[ModelArk image generation documentation](https://docs.byteplus.com/en/docs/modelark/image-generation-api)
