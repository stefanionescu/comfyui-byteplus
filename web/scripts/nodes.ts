/** Node classes whose controls change with the selected option, and the inputs that drive them. */
export const dynamicControlInputs: ReadonlyMap<string, readonly string[]> = new Map([
  ['BytePlusChatAsk', ['temperature', 'top_p', 'frequency_penalty', 'presence_penalty']],
]);
