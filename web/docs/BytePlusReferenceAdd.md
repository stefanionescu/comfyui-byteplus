# Reference: Add

Adds one file that ModelArk reads by address to a chain of references: a
preset character, an asset from your library, or a public `https://` address.
Chain several of these nodes to add several files. It sends nothing.

## Inputs

| Input        | What it takes                                                                                                 |
| ------------ | ------------------------------------------------------------------------------------------------------------- |
| `references` | References from another **Reference: Add**, **Image: Generate**, **Video: Generate**, or **Video: Download**. |
| `kind`       | What the file is: image, video, or audio. A preset character is an image.                                     |
| `url`        | An asset ID (`asset-…`), an asset URI (`asset://asset-…`), or a public `https://` address.                    |

## Outputs

| Output       | What it carries                       |
| ------------ | ------------------------------------- |
| `references` | The earlier references plus this one. |

## Use

1. In the ModelArk console, open **Playground**, choose Seedance 2.5, and open
   the **Digital characters** tab.
2. Open a character, copy its **asset ID**, and paste it into **url**.
3. Connect **references** to **Video: Generate**, and name the character in its
   prompt by its place among the images, such as "the person in Image 2".

Asset IDs work only in **Video: Generate** with Seedance 2.5 and 2.0-series
models; every other node takes `https://` addresses and ModelArk outputs.
BytePlus allows content made with preset characters only for trying the models
and internal use. Example: **video-03-cast-a-preset-character**.

[BytePlus digital character library](https://docs.byteplus.com/en/docs/modelark/avatar-library)
