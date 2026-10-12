// Shared engine contract for Firmware Lab's existing iframe player.
// A real FM-1 firmware port must explicitly advertise its capabilities.
export const CONTRACT = 'fm1-engine-v1';
export const REQUIRED = ['lcd','buttons','encoders','keys','audio'];
export function classifyPackage(pkg) {
  if (!pkg) return {kind:'missing',missing:REQUIRED};
  const manifest=pkg.fm1Engine;
  if (!manifest || manifest.contract!==CONTRACT) return {kind:'browser-app',missing:REQUIRED};
  const capabilities=manifest.capabilities||{};
  const missing=REQUIRED.filter(k=>capabilities[k]!==true);
  return {kind:missing.length?'partial-port':'hardware-port',missing};
}
export function packageDescription(pkg){
  const result=classifyPackage(pkg);
  if(result.kind==='hardware-port') return 'FM-1 hardware port installed. Safari playback and control verification still required.';
  if(result.kind==='partial-port') return 'Partial FM-1 port: missing '+result.missing.join(', ')+'.';
  if(result.kind==='browser-app') return 'Browser application installed; this is not yet an FM-1 hardware emulator.';
  return 'No browser engine installed.';
}
