import { app } from '../../scripts/app.js';

/** The text the extension's dialogs show, addressed by dotted key. */
const TEXT = {
  close: 'Close',
  settings: {
    clearKey: 'Clear Saved Key',
    close: 'Close BytePlus settings',
    credentialLabel: 'ModelArk API key',
    credentials: 'Credentials',
    environmentKey: 'Set by ARK_API_KEY',
    invalidDefinition: 'ComfyUI returned an invalid BytePlus setting definition.',
    invalidLimit: 'ComfyUI returned an invalid BytePlus limit.',
    invalidResponse: 'ComfyUI returned an invalid BytePlus settings response.',
    keyCleared: 'Saved key cleared.',
    keyNotice:
      'Add a ModelArk API key to use the extension. Create one on the API keys page of the ModelArk console. Your key stays on your ComfyUI server and is sent only to BytePlus.',
    keySaved: 'Key saved.',
    limits: 'Request limits',
    limitsSaved: 'Limits saved.',
    reread: 'Settings loaded.',
    reading: 'Loading settings...',
    noLimitChanges: 'No limit changes to save.',
    readOnly: "Changes are disabled in this host's multi-user mode.",
    reload: 'Reload Settings',
    saveFailed: 'ComfyUI could not save BytePlus settings.',
    saveKey: 'Save Key',
    saveLimits: 'Save Limits',
    savedKey: 'Saved key',
    title: 'BytePlus Settings',
    unreachable: 'Cannot reach BytePlus settings. Check ComfyUI and try again.',
    unreadableResponse: 'ComfyUI returned an unreadable BytePlus settings response.',
    updateFailed: 'BytePlus settings could not be saved.',
    readFailed: 'ComfyUI could not read BytePlus settings.',
    removeFailed: 'ComfyUI could not clear the saved ModelArk key.',
    menu: 'BytePlus settings',
  },
  working: 'Working...',
} as const;

/** Labels of the server's execution limits, keyed by setting name. */
export const LIMIT_LABELS = new Map<string, string>([
  ['max_download_megabytes', 'maximum download size (MB)'],
  ['max_upload_megabytes', 'maximum upload size (MB)'],
  ['request_timeout_seconds', 'request timeout (seconds)'],
]);

type MessagePaths<Messages> = {
  [Key in keyof Messages & string]: Messages[Key] extends string
    ? Key
    : `${Key}.${MessagePaths<Messages[Key]>}`;
}[keyof Messages & string];

export type MessageKey = MessagePaths<typeof TEXT>;

/**
 * Read one message.
 * @param key - A dotted path into the extension's text.
 * @returns The message.
 */
export function message(key: MessageKey): string {
  let value: unknown = TEXT;
  for (const part of key.split('.')) {
    // eslint-disable-next-line security/detect-object-injection -- The key is a literal path checked by its type.
    value = (value as Record<string, unknown>)[part];
  }
  return String(value);
}

/**
 * Replace an element's text.
 * @param target - The element whose text the extension owns.
 * @param content - The new text.
 */
export function setText(target: HTMLElement, content: string): void {
  // reason: The content becomes a Text node, never parsed HTML.
  // bearer:disable javascript_lang_dangerous_insert_html
  target.replaceChildren(document.createTextNode(content));
}

/**
 * Read the language ComfyUI shows, which the server's messages follow.
 * @returns A valid language tag, or English when the setting is invalid.
 */
export function selectedLocale(): string {
  const value = app.extensionManager.setting.get('Comfy.Locale');
  try {
    return (
      Intl.getCanonicalLocales(typeof value === 'string' ? value.replaceAll('_', '-') : 'en')[0] ??
      'en'
    );
  } catch {
    return 'en';
  }
}
