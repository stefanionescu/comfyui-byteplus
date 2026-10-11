# Search: Embed

Turns lines of text, images, and videos into embeddings, and compares each one
with the first.

## Inputs

| Input          | What it takes                                                                                                                                                                                   |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`        | An embedding model ID from the ModelArk model list; the default is `skylark-embedding-vision-251215`.                                                                                           |
| `images`       | Images: one, a batch, or a list. Each image is one item.                                                                                                                                        |
| `videos`       | Videos: one or a list, each up to 50 MB as MP4. Each video is one item; its sound is not read.                                                                                                  |
| `dimensions`   | The embedding length: `1024` or `2048`. `model default` is 2048.                                                                                                                                |
| `instructions` | ModelArk's instructions, sent as written with every item, such as `Target_modality: image.`, `Instruction:…`, and `Query:` on three lines. Leave it empty to let ModelArk choose for each item. |
| `run_number`   | Change it to send the same requests again.                                                                                                                                                      |
| `options`      | Settings from **Request Options**.                                                                                                                                                              |
| `texts`        | One item per line. Blank lines are skipped.                                                                                                                                                     |

## Outputs

| Output         | What it carries                                                                             |
| -------------- | ------------------------------------------------------------------------------------------- |
| `vectors`      | A JSON list with one embedding per item: the texts first, then the images, then the videos. |
| `similarities` | A JSON list of each item's cosine similarity to the first item.                             |

## Use

1. Write one item per line, with the item to compare against first.
2. Connect `similarities` to **Preview as Text**.
3. Select **Run**.

Each item is its own request, sent one after another. If one fails, the rest
are not sent.
Example: **search-01-choose-a-hero-image**.

[ModelArk embedding documentation](https://docs.byteplus.com/en/docs/modelark/vectorization)
