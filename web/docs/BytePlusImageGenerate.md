# Image: Generate

Generates or edits images with any Seedream model on BytePlus ModelArk, and
outputs each image's ModelArk address as a reference.

## Inputs

| Input                 | What it takes                                                                                                                                                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `model`               | Any Seedream model ID from the ModelArk model list; the default is `dola-seedream-5-0-flash-260915`.                                                                                 |
| `size`                | `1K`, `1.5K`, `2K`, `3K`, or `4K`. **model default** is 2K.                                                                                                                          |
| `aspect_ratio`        | The shape, such as `16:9`. **model default** lets the model take the shape from the prompt.                                                                                          |
| `count`               | The most images to make, 1 to 15. Above 1, only models that make image series take it; ask for that many in the prompt, such as "Generate 4 images of …", or the model may make one. |
| `background`          | `transparent` keeps the transparency of one reference image that has it, such as one from **Join Image with Alpha**, and makes a PNG.                                                |
| `output_format`       | `png` or `jpeg`. **model default** is JPEG. Seedream 4.5 and 4.0 always make JPEG.                                                                                                   |
| `prompt_optimization` | `standard` or `fast`. Fast answers sooner with slightly lower quality, on models that offer it.                                                                                      |
| `watermark`           | Adds an AI-generated mark in the lower right corner.                                                                                                                                 |
| `reference_images`    | Images to edit or combine: one, a batch, or a list, each at its own size. They are Image 1, Image 2, and so on, before any **references**.                                           |
| `references`          | Image references from **Image: Generate**, **Video: Generate**, or **Reference: Add**. Assets are refused.                                                                           |
| `run_number`          | Change it to send the same request again.                                                                                                                                            |
| `prompt`              | What to draw or change. Name references as Image 1, Image 2, and so on.                                                                                                              |
| `options`             | Settings from **Request Options**.                                                                                                                                                   |

**model default** sends nothing, except for **size**, which always sends a
size. Before anything is paid, the node refuses a size, shape, count, format,
or number of references the model does not take, naming what it does take.

## Outputs

| Output       | What it carries                                                                                |
| ------------ | ---------------------------------------------------------------------------------------------- |
| `images`     | The images, each at its own size.                                                              |
| `masks`      | One mask per image, from its transparency. White is transparent; opaque images are all black.  |
| `references` | Each image's ModelArk address, valid for 24 hours, so another node can send the original file. |

## Use

1. Write the prompt and type the model ID.
2. Connect any reference images or references.
3. Connect **images** to **Save Image**, and select **Run**. To start a video
   from an image, connect **references** to **first frame** on **Video:
   Generate**.

Examples: **image-01-design-a-character** and
**image-02-make-a-poster-series**. Seedance trusts faces in images Seedream 5.0
made from text for 30 days, but only in the original file, so connect
**references**, not **images**.

[ModelArk image generation documentation](https://docs.byteplus.com/en/docs/modelark/image-generation-api)
