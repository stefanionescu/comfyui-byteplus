# Request Options

Sets the service tier and extra request fields for any number of paid nodes.

## Inputs

| Input          | What it takes                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------- |
| `tier`         | `model default` sends nothing; `flex` asks for ModelArk's lower-cost tier, which queues requests. |
| `extra_fields` | A JSON object of fields added to the request as written, such as `{"priority": 5}`.               |

## Outputs

| Output    | What it carries                              |
| --------- | -------------------------------------------- |
| `options` | The settings, for a paid node's **options**. |

## Use

1. Choose a tier or write extra fields, and leave the rest at their defaults.
2. Connect **options** to the **options** input of one or more paid nodes.

A paid node checks the options before it sends, and stops with an error when:

- **tier** is `flex` and its request takes no tier: images, layers,
  embeddings, and 3D take none;
- **tier** is `flex` and its model does not take flex;
- **extra fields** sets a field the node sets itself.

The models that take flex:

| Model                          | Node            |
| ------------------------------ | --------------- |
| `dola-seed-2-1-turbo-260628`   | Chat: Ask       |
| `deepseek-v4-pro-ga-260813`    | Chat: Ask       |
| `deepseek-v4-flash-ga-260731`  | Chat: Ask       |
| `seedance-1-0-pro-250528`      | Video: Generate |
| `seedance-1-0-pro-fast-251015` | Video: Generate |
| `seedance-1-5-pro-251215`      | Video: Generate |

**Model: Info** shows `"flex": true` for each of them.

A chat request on flex waits in ModelArk's queue for up to 20 minutes; set
the request timeout in **BytePlus settings** longer than that. A video task
on flex can wait for hours: the node records it, and **Video: Download**
collects it. A task still unfinished 48 hours after it was created expires,
and ModelArk charges nothing for it.

The fields each node sets itself, which extra fields cannot replace:

| Node                | Fields                                                                                                                                             |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Chat: Ask           | model, messages, stream, stream_options, service_tier                                                                                              |
| Image: Generate     | model, prompt, image, response_format, stream, layer_decomposition, sequential_image_generation, sequential_image_generation_options, service_tier |
| Image: Split Layers | the same as Image: Generate                                                                                                                        |
| Video: Generate     | model, content, callback_url, return_last_frame, service_tier                                                                                      |
| 3D: Generate        | model, content, callback_url, service_tier                                                                                                         |
| Search: Embed       | model, input, encoding_format, service_tier                                                                                                        |

Any other field goes to ModelArk as written, unchecked; ModelArk refuses a
field the model does not take, and charges nothing for a refused request.

[ModelArk flex tier documentation](https://docs.byteplus.com/en/docs/modelark/online-inference-flex)
