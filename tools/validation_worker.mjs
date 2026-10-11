// Each worker runs one unchanged verifier and is terminated by the parent.
self.onmessage = async ({ data: { suite, wasm } }) => {
  try {
    const [, modulePath, functionName, fixturePaths] = suite;
    const load = async name => {
      const response = await fetch(name);
      if (!response.ok) throw new Error(name + ': HTTP ' + response.status);
      return new Uint8Array(await response.arrayBuffer());
    };
    const loadJSON = async name => JSON.parse(new TextDecoder().decode(await load(name)));
    const fixtures = typeof fixturePaths === 'string'
      ? await loadJSON(fixturePaths)
      : Object.fromEntries(await Promise.all(Object.entries(fixturePaths)
        .map(async ([key, path]) => [key, await loadJSON(path)])));
    const verifier = (await import(modulePath))[functionName];
    const extra = functionName === 'verifyCompression'
      ? (await import('./script-state-checks.mjs')).verifyScriptState : undefined;
    const result = await verifier(wasm, fixtures, load, extra);
    self.postMessage({ result });
  } catch (error) {
    self.postMessage({ error: error.stack || String(error) });
  }
};
