# Model: Info

Shows what the extension knows about a BytePlus model ID: what the model
reads, makes, and takes, as JSON. It reads the model table bundled with the
extension, so it is free and needs no key.

## Inputs

| Input   | What it takes                                                                     |
| ------- | --------------------------------------------------------------------------------- |
| `model` | Any model ID from the ModelArk model list; the default is `seed-2-0-lite-260428`. |

## Outputs

| Output | What it carries                                      |
| ------ | ---------------------------------------------------- |
| `info` | The model's row as JSON, with the keys listed below. |

The paid nodes check each request against the same row before paying, so
**info** holds exactly what they accept.

| Key          | What it holds                                                                                                                         |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| model        | The ID as typed. Nodes send exactly this ID.                                                                                          |
| row          | The model the row describes.                                                                                                          |
| matched      | `exact`, or `family`: a newer version than the table knows, checked against its family's newest row.                                  |
| kinds        | The nodes that take the model: `chat`, `image`, `layers`, `video`, `embedding`, `3d`.                                                 |
| family       | The model ID without its six-digit version, such as `seed-2-0-lite`.                                                                  |
| status       | `current`; `deprecated`, replaced by a newer version; or `retiring`, ending without one.                                              |
| deactivation | The date BytePlus stops serving the model, or `null`.                                                                                 |
| replacement  | The model BytePlus recommends instead, or `null`.                                                                                     |
| inputs       | What the model reads: `text`, `image`, `video`, `audio`, `pdf`.                                                                       |
| outputs      | What it makes: `text`, `image`, `video`, `embedding`, `3d`.                                                                           |
| flex         | Whether it takes the flex tier in **Request Options**.                                                                                |
| limits       | What the node may ask of it, such as reasoning effort and token limits for chat, or resolutions, durations, and references for video. |
| sources      | The BytePlus pages the row was read from, with each page's update date.                                                               |

For example, part of the report for `seed-2-0-lite-260428`:

```json
{
    "model": "seed-2-0-lite-260428",
    "row": "seed-2-0-lite-260428",
    "matched": "exact",
    "kinds": ["chat"],
    "inputs": ["audio", "image", "pdf", "text", "video"],
    "flex": false,
    "limits": {
        "max_output": 131072,
        "thinking": ["enabled", "disabled"],
        "has_effort": true,
        "default_effort": "medium"
    }
}
```

## Use

1. Type or connect the model ID.
2. Connect **info** to **Preview as Text** to read it, or to **Extract Text
   from JSON** to use one top-level key.

Another extension can run the node and read **info** instead of copying a
model's limits; the advanced guide explains how.

Example: **image-02-make-a-poster-series**.

[ModelArk model list](https://docs.byteplus.com/en/docs/modelark/model-list)
