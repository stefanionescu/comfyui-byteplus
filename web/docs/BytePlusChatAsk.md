# Chat: Ask

Asks a ModelArk chat model a question, with images, video, audio, or
documents if the model reads them. Returns the answer, the model's reasoning,
and the conversation so far.

## Inputs

| Input                   | What it takes                                                                                                                                                                                       |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                 | Any chat model ID from the ModelArk model list; the default is `seed-2-0-lite-260428`.                                                                                                              |
| `conversation`          | Earlier turns, from another **Chat: Ask**.                                                                                                                                                          |
| `documents`             | Files from **Chat: Attach Document**.                                                                                                                                                               |
| `images`                | Images: one, a batch, or a list. Each is sent as PNG at its own size.                                                                                                                               |
| `videos`                | Videos: one or a list. Each is sent as MP4.                                                                                                                                                         |
| `audio`                 | Audio clips, for models that read audio, such as `seed-2-0-lite-260428` and `seed-2-0-mini-260428`. Each is sent as WAV.                                                                            |
| `references`            | Image, video, and audio references from **Image: Generate**, **Video: Generate**, or **Reference: Add**. Assets are refused.                                                                        |
| `thinking`              | `enabled` or `disabled` turns reasoning on or off, on models that take it. `disabled` is faster and costs less.                                                                                     |
| `reasoning_effort`      | How much the model thinks: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, or `max`. Each model maps these to the levels it has. With `thinking` set to `disabled`, only `minimal` is allowed. |
| `max_completion_tokens` | The most tokens the model may write, reasoning included, up to 65,536. 0 sends nothing, so the model's default applies: 4,096 answer tokens for most models, with reasoning not counted.            |
| `temperature`           | `default` sends none. `custom` sends `value`, from 0 to 2; higher values vary the answer more.                                                                                                      |
| `top_p`                 | `default` sends none. `custom` sends a share from 0 to 1 of the likely words the model picks from.                                                                                                  |
| `frequency_penalty`     | `default` sends none. `custom` sends a value from -2 to 2; above 0, a word repeats less the more often it has appeared.                                                                             |
| `presence_penalty`      | `default` sends none. `custom` sends a value from -2 to 2; above 0, any word that has appeared repeats less.                                                                                        |
| `run_number`            | Change this number to send the same request again.                                                                                                                                                  |
| `options`               | Settings from **Request Options**.                                                                                                                                                                  |
| `json_schema`           | The `response_format.json_schema` object: a `name` and the `schema` the answer must follow, with `strict` if you want it. Leave it empty for free text.                                             |
| `stop`                  | Text that ends the answer, one per line, for the DeepSeek V4.1 Flash and V4 GA models. Leave it empty to send none.                                                                                 |
| `prompt`                | The question or instruction.                                                                                                                                                                        |
| `system_prompt`         | The system prompt: instructions for the whole answer.                                                                                                                                               |

## Outputs

| Output         | What it carries                                                                                                  |
| -------------- | ---------------------------------------------------------------------------------------------------------------- |
| `text`         | The answer.                                                                                                      |
| `reasoning`    | The model's reasoning, or a summary of it from some Seed models. Connected nodes are skipped when there is none. |
| `conversation` | The earlier turns plus this question and answer, for the next **Chat: Ask**.                                     |

## Use

1. Write the prompt and type the model ID.
2. Connect any media the model reads.
3. Connect `text` to **Preview as Text**, and select **Run**.

Examples: **chat-01-write-a-product-listing** and
**chat-02-summarize-a-voice-note**.

Everything connected goes in one request. To ask about the same media in a
later turn, connect it again.

Before you pay anything, the node refuses:

- media the model does not read;
- a `thinking` or `reasoning_effort` value the model does not take;
- a sampling setting or `stop` that the model ignores;
- a `json_schema` the model cannot follow.

DeepSeek V4.1 Flash uses `top_p` only while it thinks, and DeepSeek V4 Pro and
Flash use the penalties only with `thinking` set to `disabled`.

An answer that stops mid-sentence hit the token limit; raise
`max_completion_tokens`.

[ModelArk chat documentation](https://docs.byteplus.com/en/docs/modelark/chat-api)
