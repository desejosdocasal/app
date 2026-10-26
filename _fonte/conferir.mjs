// Confere as cartas de um idioma contra o português: mesma estrutura e metadados, sem português sobrando, sem palavrão,
// sem travessão, sem artigo antes de {par}. Rodar da pasta do app: node _fonte/conferir.mjs it-IT
import fs from 'node:fs';
const LINGUA = process.argv[2] || 'it-IT';
const ler = (l) => { const d = `conteudo/${l}`, c = { vd: {} }; for (const n of fs.readdirSync(d).filter(n => n.endsWith('.json'))) { const j = JSON.parse(fs.readFileSync(`${d}/${n}`, 'utf8')); n.startsWith('vd-') ? Object.assign(c.vd, j) : Object.assign(c, j); } return c; };
const pt = ler('pt-BR'), it = ler(LINGUA), prob = [];
const meta = new Set(['seg', 'nivel', 'tipo', 'fase']);
function cmp(a, b, p) {
  if (b === undefined) { prob.push('falta ' + p); return; }
  if (Array.isArray(a)) { if (!Array.isArray(b) || a.length !== b.length) prob.push(`tamanho ${p}: ${a.length} x ${b?.length}`); else a.forEach((x, i) => cmp(x, b[i], `${p}[${i}]`)); return; }
  if (a && typeof a === 'object') { for (const k of Object.keys(a)) { if (meta.has(k)) { if (a[k] !== b[k]) prob.push(`meta ${p}.${k}: ${a[k]} x ${b[k]}`); } else cmp(a[k], b[k], `${p}.${k}`); } for (const k of Object.keys(b)) if (!(k in a)) prob.push('sobra ' + p + '.' + k); return; }
  if (typeof b !== 'string' || !b.trim()) prob.push('vazio ' + p);
}
const jogos = Object.keys(pt).filter(k => k in it);
for (const k of jogos) cmp(pt[k], it[k], k);
const textos = []; (function w(o, p) { if (typeof o === 'string') textos.push([p, o]); else if (Array.isArray(o)) o.forEach((x, i) => w(x, p + '[' + i + ']')); else if (o && typeof o === 'object') for (const k in o) if (!meta.has(k)) w(o[k], p + '.' + k); })(Object.fromEntries(jogos.map(k => [k, it[k]])), '');
const PT = /ç|ã|õ|ê|ô|\b(não|pra|uma|beije|conte|seu|com o|do seu|então|também)\b|você|vocês|nh|lh/i;
const VULG = /\b(fica|fiche|figa|scopa|scopare|scopate|scopi|cazz\w*|troia|minchia|sega|seghe|uccello|passera|patata|pompino|culo|tette)\b/i;
const out = { pt: [], vulg: [], dash: [], par: [] };
for (const [p, t] of textos) {
  if (PT.test(t.replace(/papel_voce/g, ''))) out.pt.push(p + ': ' + t);
  if (VULG.test(t)) out.vulg.push(p + ': ' + t);
  if (/[–—]/.test(t)) out.dash.push(p);
  if (/\b(il|la|lo|al|alla|del|della|dal|dalla|col|nel|sul)\s+\{par\}/i.test(t)) out.par.push(p + ': ' + t);
}
console.log('jogos conferidos:', jogos.join(', '), '| textos:', textos.length);
console.log('estrutura e metadados:', prob.length ? prob.slice(0, 15) : 'ok');
for (const [k, v] of Object.entries(out)) console.log(k, v.length, v.slice(0, 8));
