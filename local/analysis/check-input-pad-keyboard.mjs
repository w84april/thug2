import assert from 'node:assert/strict';
import {bindKeyboardInput,keyboardPacketButtons} from '../../src/platform/browser_input.mjs';
class Surface extends EventTarget {
  constructor(){super();this.ownerDocument=new EventTarget();this.ownerDocument.defaultView=new EventTarget();}
}
const surface=new Surface();let changes=0;
const input=bindKeyboardInput(surface,()=>changes++);
function key(type,code,properties={}){
 const event=new Event(type,{cancelable:true});Object.assign(event,{code,...properties});surface.dispatchEvent(event);return event;
}
assert.deepEqual([...input.packet.slice(0,4)],[128,128,128,128]);
assert.deepEqual([...input.packet.slice(18,22)],[128,128,128,128]);
for(const [code,index] of Object.entries(keyboardPacketButtons)){
 assert(key('keydown',code).defaultPrevented);assert.equal(input.packet[index],255);
 const before=changes;key('keydown',code,{repeat:true});assert.equal(changes,before);
 key('keyup',code);assert.equal(input.packet[index],0);
}
assert(!key('keydown','KeyA').defaultPrevented);
key('keydown','Space',{isComposing:true});assert.equal(input.packet[10],0);
key('keydown','ArrowUp');key('keydown','Space');assert.equal(input.packet[6],255);assert.equal(input.packet[10],255);
surface.dispatchEvent(new Event('blur'));assert.equal(input.packet[6],0);assert.equal(input.packet[10],0);
key('keydown','Space');surface.ownerDocument.defaultView.dispatchEvent(new Event('blur'));assert.equal(input.packet[10],0);
key('keydown','Space');surface.ownerDocument.hidden=true;surface.ownerDocument.dispatchEvent(new Event('visibilitychange'));assert.equal(input.packet[10],0);
key('keydown','Space');input.destroy();assert.equal(input.packet[10],0);const before=changes;
key('keydown','Space');assert.equal(input.packet[10],0);assert.equal(changes,before);
console.log('PASS: keyboard mapping, combinations, repeat, focus loss, hidden page and cleanup');
