import '#web/interface.css';
import { message } from '#web/text.ts';
import { app } from '../../scripts/app.js';
import { requestLocal } from '#web/http.ts';
import { dynamicControlInputs } from '#web/nodes.ts';
import { openSettings } from '#web/settings/dialog.ts';
import type { Widget, CanvasNode } from '#web/contracts.ts';

const controlRestorers = new WeakMap<CanvasNode, ((restore?: boolean) => void)[]>();

/**
 * Restore the value a child widget held under the current option, and save its value when the option leaves.
 *
 * Checked on frontend 1.52.7: the host resets a child widget to its default when its option returns.
 *
 * @param canvasNode - The node that owns the dropdown.
 * @param child - A widget that the current option shows.
 * @param key - The current option and the name of the child, joined by a slash.
 * @param restore - Whether to put the saved value back.
 */
function keepChildValue(canvasNode: CanvasNode, child: Widget, key: string, restore: boolean): void {
    const saved = canvasNode.properties.conditionalValues;
    if (restore && saved && Object.hasOwn(saved, key)) child.value = saved[key];
    const removed = child.onRemove?.bind(child);
    child.onRemove = () => {
        if (!app.configuringGraph) {
            canvasNode.properties.conditionalValues ??= {};

            canvasNode.properties.conditionalValues[key] = child.value;
        }
        removed?.();
    };
}

/**
 * Keep the values of hidden controls in the properties of the node.
 *
 * @param canvasNode - The node that owns the conditional widgets.
 * @param widget - The dynamic dropdown of ComfyUI.
 * @returns A callback that restores the widgets of the current option and watches for new ones.
 */
function preserveControlValues(canvasNode: CanvasNode, widget: Widget): (restore?: boolean) => void {
    const restoredWidgets = new WeakSet<Widget>();
    const restoreValues = (restore = false): void => {
        const selected = widget.value as string;
        for (const child of canvasNode.widgets ?? []) {
            if (!child.name.startsWith(`${widget.name}.`) || restoredWidgets.has(child)) continue;
            restoredWidgets.add(child);
            keepChildValue(canvasNode, child, `${selected}/${child.name}`, restore);
        }
    };
    restoreValues();
    return restoreValues;
}

/**
 * Restore the hidden values of a control whenever its option changes, after the handler of ComfyUI has run, and
 * redraw the Parameters panel.
 *
 * @param canvasNode - The node that owns the control.
 * @param widget - The dynamic dropdown of ComfyUI.
 * @returns The callback that restores the current option of this control.
 */
function watchControl(canvasNode: CanvasNode, widget: Widget): (restore?: boolean) => void {
    const restoreValues = preserveControlValues(canvasNode, widget);
    const previous = widget.callback?.bind(widget);
    widget.callback = (...args) => {
        previous?.(...args);
        restoreValues(true);
        // Checked on frontend 1.52.7: the Parameters panel keeps the rows of the previous option until the selection changes.
        const canvas = app.canvas;
        // eslint-disable-next-line @typescript-eslint/no-deprecated -- reason: ComfyUI offers no other way to refresh the Parameters panel.
        canvas.onSelectionChange?.(canvas.selected_nodes);
    };
    return restoreValues;
}

/**
 * Keep the conditional values of a node across option changes.
 *
 * @param canvasNode - The node ComfyUI created.
 */
function addNodeControls(canvasNode: CanvasNode): void {
    const restorers: ((restore?: boolean) => void)[] = [];
    for (const name of dynamicControlInputs.get(canvasNode.comfyClass ?? '') ?? []) {
        const widget = canvasNode.widgets?.find((candidate) => candidate.name === name);
        if (widget) restorers.push(watchControl(canvasNode, widget));
    }
    controlRestorers.set(canvasNode, restorers);
}

/** Watch the conditional values of every node after the graph changes. */
function refreshGraph(): void {
    for (const canvasNode of app.rootGraph.nodes) {
        for (const restoreValues of controlRestorers.get(canvasNode) ?? []) restoreValues();
    }
}

app.registerExtension({
    name: 'byteplus',
    setup: () => {
        const stylesheet = document.createElement('link');
        stylesheet.rel = 'stylesheet';
        stylesheet.href = new URL('extension.css', import.meta.url).href;
        const stylesheets = new Set();
        for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
            stylesheets.add(link.getAttribute('href'));
        }
        if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
    },
    nodeCreated: addNodeControls,
    afterConfigureGraph: refreshGraph,
    commands: [
        {
            id: 'BytePlus.OpenSettings',
            label: message('settings.menu'),
            function: openSettings.bind(null, requestLocal),
        },
    ],
    menuCommands: [
        {
            path: ['Extensions', 'BytePlus'],
            commands: ['BytePlus.OpenSettings'],
        },
    ],
});
