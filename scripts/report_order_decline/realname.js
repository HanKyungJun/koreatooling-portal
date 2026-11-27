// 실명판 만들기 (REAL=1 일 때만). 대조표는 wiki/_private/거래처_익명코드표.csv(gitignore)에서 읽음 — 이 파일에는 실명 없음
const fs = require('fs'), path = require('path');
const ON = process.env.REAL === '1';
let MAP = {};
if (ON) {
  const csv = fs.readFileSync(path.join(__dirname, '..', '..', 'wiki', '_private', '거래처_익명코드표.csv'), 'utf8').replace(/^﻿/, '').trim().split(/\r?\n/);
  const hd = csv[0].split(',');
  csv.slice(1).forEach((l) => { const c = l.split(','); MAP[c[hd.indexOf('code')]] = c[hd.indexOf('core')]; });
}
const bat = (name) => { const ch = name.charCodeAt(name.length - 1); return ch >= 0xAC00 && ch <= 0xD7A3 ? (ch - 0xAC00) % 28 : 0; };
const josa = (name, p) => {
  if (!p) return '';
  const b = bat(name), has = b !== 0;
  if (p === '은' || p === '는') return has ? '은' : '는';
  if (p === '이' || p === '가') return has ? '이' : '가';
  if (p === '을' || p === '를') return has ? '을' : '를';
  if (p === '과' || p === '와') return has ? '과' : '와';
  if (p === '으로' || p === '로') return has && b !== 8 ? '으로' : '로';
  return p;
};
const RE = /거래처 ([A-Z]{1,2})(?![A-Za-z])((?:(?:, |와 |과 )[A-Z]{1,2}(?![A-Za-z]))*)(으로|[은는이가을를과와의로])?/g;
function apply(t) {
  if (!ON || typeof t !== 'string') return t;
  return t.replace(RE, (m, first, rest, p) => {
    const codes = [first]; const joins = [];
    (rest.match(/(, |와 |과 )([A-Z]{1,2})/g) || []).forEach((s) => { const mm = s.match(/(, |와 |과 )([A-Z]{1,2})/); joins.push(mm[1].trim()); codes.push(mm[2]); });
    const names = codes.map((c) => MAP['거래처 ' + c] || ('거래처 ' + c));
    let out = names[0];
    for (let i = 1; i < names.length; i++) out += (joins[i - 1] === ',' ? ', ' : josa(names[i - 1], joins[i - 1]) + ' ') + names[i];
    return out + (p === '의' ? '의' : josa(names[names.length - 1], p));
  });
}
module.exports = { apply, ON, MAP };
