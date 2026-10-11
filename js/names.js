// Presentation-only names; canonical IDs remain unchanged for installed packages.
export function firmwareTitle(f) {
  const id = String(f?.id || '').toLowerCase();
  const names = {
    'zp12':'ZP12', 'felucca':'Felucca', 'felucca-salt':'Felucca Salt',
    'sloop':'SLOOP', 'sloopdx':'SLOOP DX', 'x0x':'FM1-X0X',
    'sloop-floyd-fm':'SLOOP Floyd FM', 'sloop-dx7-banks':'SLOOP DX7 Banks',
    'fomni':'FoMni', 'fimba-1':'FiMba-1', 'ghoulbox':'GHOULBOX',
    'waveloop':'WaveLoop', 'jiant-fm':'JIANT FM', 'm-vave-official':'M-VAVE Official'
  };
  if (names[id]) return names[id];
  let name=String(f?.name || f?.id || 'Unknown firmware')
    .replace(/\s*[\[(]\s*(?:v(?:ersion)?\s*)?\d+(?:\.\d+)*(?:[-.][\w]+)?\s*[\])]\s*$/i,'')
    .replace(/\s+(?:v(?:ersion)?\s*)?\d+(?:\.\d+)*(?:[-.][\w]+)?\s*$/i,'')
    .replace(/\s+/g,' ').trim();
  return name || String(f?.id || 'Unknown firmware');
}
export function firmwareDescription(f) {
  const desc=String(f?.what || f?.description || '').trim();
  if (!desc || /^browser build required before/i.test(desc))
    return 'Community FM-1 firmware; a browser-compatible engine is required to play in the Lab.';
  return desc;
}
