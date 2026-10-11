// Browser adapter, not recovered game code. The engine consumes this packet
// through the original 0046bda0 decoder each frame. Bind to the focused game
// surface so typing elsewhere does not change the skater's input.
export const keyboardPacketButtons = Object.freeze({
  ArrowUp: 6, ArrowDown: 7, ArrowLeft: 5, ArrowRight: 4,
  Space: 10, KeyZ: 11, KeyX: 9, KeyC: 8,
});

export function bindKeyboardInput(surface, onChange = () => {}) {
  const packet = new Uint8Array(32);
  packet.fill(128, 0, 4);
  packet.fill(128, 0x12, 0x16);
  const held = new Set();
  const change = (event) => {
    const index = keyboardPacketButtons[event.code];
    if (index === undefined || event.isComposing) return;
    event.preventDefault();
    const down = event.type === 'keydown';
    if (held.has(event.code) === down) return;
    down ? held.add(event.code) : held.delete(event.code);
    packet[index] = down ? 255 : 0;
    onChange(packet);
  };
  const release = () => {
    if (!held.size) return;
    for (const code of held) packet[keyboardPacketButtons[code]] = 0;
    held.clear();
    onChange(packet);
  };
  const window = surface.ownerDocument.defaultView;
  const document = surface.ownerDocument;
  const visibility = () => { if (document.hidden) release(); };
  surface.addEventListener('keydown', change);
  surface.addEventListener('keyup', change);
  surface.addEventListener('blur', release);
  window.addEventListener('blur', release);
  document.addEventListener('visibilitychange', visibility);
  return {
    packet,
    destroy() {
      surface.removeEventListener('keydown', change);
      surface.removeEventListener('keyup', change);
      surface.removeEventListener('blur', release);
      window.removeEventListener('blur', release);
      document.removeEventListener('visibilitychange', visibility);
      release();
    },
  };
}
