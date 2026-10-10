# Chat: Ask

Asks a ModelArk chat model a question, with images, video, audio, or
documents if the model reads them. Returns the answer, the model's reasoning,
and the conversation so far.

## Inputs

| Input              | What it takes                                                                                                                                                                                        |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`            | Any chat model ID from the ModelArk model list; the default is `seed-2-0-lite-260428`. A chat model newer than the extension also works, without **thinking**, **reasoning effort**, or PDFs.        |
| `conversation`     | Earlier turns, from another **Chat: Ask**.                                                                                                                                                           |
| `documents`        | Files from **Chat: Attach Document**. PDFs need a model that reads them; text files go to any model.                                                                                                 |
| `images`           | Images: one, a batch, or a list. Each is sent as PNG at its own size, up to 10 MB.                                                                                                                   |
| `videos`           | Videos: one or a list. Each is sent as MP4, up to 50 MB.                                                                                                                                             |
| `audio`            | Audio clips, for models that read audio, such as `seed-2-0-lite-260428` and `seed-2-0-mini-260428`. Each is sent as WAV, up to 25 MB.                                                                |
| `references`       | Image, video, and audio references from **Image: Generate**, **Video: Generate**, or **Reference: Add**. Assets are refused.                                                                         |
| `thinking`         | **on** or **off** turns the model's reasoning on or off. **model default** leaves it to the model, and most models think by default. Off is faster and costs less.                                   |
| `reasoning_effort` | How much the model reasons: **none**, **minimal**, **low**, **medium**, **high**, **xhigh**, or **max**. Each model maps these to the levels it has. With thinking off, only **minimal** is allowed. |
| `max_tokens`       | The most tokens the model may write, reasoning included, up to 65,536. 0 keeps ModelArk's default limit of 4,096 answer tokens, with reasoning not counted.                                          |
| `temperature`      | **model default** sends none. **set** sends a value from 0 to 2; higher values vary the answer more.                                                                                                 |
| `run_number`       | Change it to send the same request again.                                                                                                                                                            |
| `options`          | Settings from **Request Options**.                                                                                                                                                                   |
| `answer_schema`    | A JSON schema the answer must follow. Leave it empty for free text.                                                                                                                                  |
| `prompt`           | The question or instruction.                                                                                                                                                                         |
| `system_prompt`    | The system prompt: instructions for the whole answer.                                                                                                                                                |

## Outputs

| Output         | What it carries                                                                                                  |
| -------------- | ---------------------------------------------------------------------------------------------------------------- |
| `text`         | The answer.                                                                                                      |
| `reasoning`    | The model's reasoning, or a summary of it from some Seed models. Connected nodes are skipped when there is none. |
| `conversation` | The earlier turns plus this question and answer, for the next **Chat: Ask**.                                     |

## Use

1. Write the prompt and type the model ID.
2. Connect any media the model reads.
3. Connect **text** to **Preview as Text**, and select **Run**.

Examples: **chat-01-write-a-product-listing** and
**chat-02-summarize-a-voice-note**.

Everything connected goes in one request: the documents, images, image
references, videos, video references, audio, and audio references, in that
order, then the prompt. To ask about the same media in a later turn, connect
it again.

Before anything is paid, the node refuses media the model does not read, a
thinking or effort choice it does not take, a temperature it ignores, an
answer schema it cannot follow, and max tokens above its longest answer.

An answer that stops mid-sentence hit the token limit; raise **max tokens**.

[ModelArk chat documentation](https://docs.byteplus.com/en/docs/modelark/chat-api)
