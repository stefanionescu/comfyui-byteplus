# Chat: Attach Document

Attaches a PDF or text file from ComfyUI's input folder to **Chat: Ask**.
Chain several of these nodes to attach several files.

## Inputs

| Input       | What it takes                                                                  |
| ----------- | ------------------------------------------------------------------------------ |
| `file`      | A PDF, text, Markdown, CSV, or JSON file at the top of ComfyUI's input folder. |
| `documents` | Documents from another **Chat: Attach Document**.                              |

## Outputs

| Output      | What it carries                                         |
| ----------- | ------------------------------------------------------- |
| `documents` | The earlier documents plus this one, for **Chat: Ask**. |

## Use

1. Put the file in ComfyUI's input folder and press R to refresh the list.
2. Choose it in **document**.
3. Connect **documents** to **Chat: Ask**.

A PDF goes to models that read PDFs; ModelArk reads each page as an image. A
text file goes to any model and must be UTF-8. An edited file is read again on
the next run. Example: **chat-01-write-a-product-listing**.

[ModelArk document understanding](https://docs.byteplus.com/en/docs/modelark/document-understanding)
