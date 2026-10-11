# Request Options

Sets the service tier and extra request fields for any number of paid nodes.

## Inputs

| Input          | What it takes                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------- |
| `service_tier` | `model default` sends nothing; `flex` asks for ModelArk's lower-cost tier, which queues requests. |
| `extra_fields` | A JSON object of fields added to the request as written, such as `{"priority": 5}`.               |

## Outputs

| Output    | What it carries                              |
| --------- | -------------------------------------------- |
| `options` | The settings, for a paid node's **options**. |

## Use

1. Choose a service tier or write extra fields, and leave the rest at their
   defaults.
2. Connect **options** to the **options** input of one or more paid nodes.

A paid node stops before sending when **service tier** is `flex` and its model
does not take flex. **Model: Info** shows `"flex": true` for each model that
takes flex. A paid node also stops when **extra fields** sets a field the node
sets itself, such as `model` or `prompt`.

Example: **chat-02-summarize-a-voice-note**.

[ModelArk flex tier documentation](https://docs.byteplus.com/en/docs/modelark/online-inference-flex)
