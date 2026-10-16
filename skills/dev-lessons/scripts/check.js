#!/usr/bin/env node
/**
 * dev-lessons 一致性校验（零依赖，Node >= 16）
 *
 * 用法:
 *   node scripts/check.js
 *
 * 检查项:
 *   1. 前缀归属: L->llm-app F->frontend-backend D->data-db U->upstream-reuse
 *                E->deploy-env C->collab-testing M->misc R->rag V->eval-method
 *   2. 编号唯一（正文与索引表各自）
 *   3. 正文 / 索引表顺序递增（抓重编号后插错位的残留）
 *   4. 索引表与正文双向一致（不多不少）
 *   5. 编号无跳号（warning）
 *   6. 卡片六字段齐全（场景/问题/根因/方案/反模式/溯源）—— 历史条目允许缺，报 warning
 *   7. SKILL.md 中声明的条数与实际一致（领域文档索引 + 使用方式段落）
 *   8. references/*.md 交叉引用无死链
 *
 * 退出码: 0 = 通过（可含 warning）；1 = 存在 error
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const REF_DIR = path.join(ROOT, 'references');
const SKILL_FILE = path.join(ROOT, 'SKILL.md');

const PREFIX_BY_FILE = {
  'llm-app.md': 'L',
  'frontend-backend.md': 'F',
  'data-db.md': 'D',
  'upstream-reuse.md': 'U',
  'deploy-env.md': 'E',
  'collab-testing.md': 'C',
  'misc.md': 'M',
  'rag.md': 'R',
  'eval-method.md': 'V',
};

const FIELDS = ['场景', '问题', '根因', '方案', '反模式', '溯源'];

const problems = [];
const add = (level, file, line, msg) => problems.push({ level, file, line, msg });
const fail = (file, line, msg) => add('error', file, line, msg);
const warn = (file, line, msg) => add('warn', file, line, msg);

const readNormalized = (p) =>
  fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n');

const lineOf = (text, index) => text.slice(0, index).split('\n').length;

const actualCounts = {};
const fileStats = [];

function checkRefFile(fileName) {
  const prefix = PREFIX_BY_FILE[fileName];
  const text = readNormalized(path.join(REF_DIR, fileName));
  const lines = text.split('\n');

  const body = [];
  const idxRows = [];
  lines.forEach((ln, i) => {
    const n = i + 1;
    let m = ln.match(/^###\s+([A-Z])-(\d+)(?=\s|$)/);
    if (m) return body.push({ id: m[1] + '-' + m[2], p: m[1], num: +m[2], line: n });
    m = ln.match(/^\|\s*([A-Z])-(\d+)\s*\|/);
    if (m) return idxRows.push({ id: m[1] + '-' + m[2], p: m[1], num: +m[2], line: n });
    m = ln.match(/^###\s+(.+)/);
    if (m) warn(fileName, n, '非条目格式的 ### 标题: ' + m[1].slice(0, 30));
  });

  // 1/2. 前缀归属 + 唯一性
  for (const pair of [['正文', body], ['索引', idxRows]]) {
    const kind = pair[0];
    const list = pair[1];
    const seen = new Map();
    for (const it of list) {
      if (it.p !== prefix) fail(fileName, it.line, kind + '条目前缀错误: ' + it.id + '（本文件应为 ' + prefix + '-）');
      if (seen.has(it.id)) fail(fileName, it.line, kind + '条目重复: ' + it.id + '（首次出现于行 ' + seen.get(it.id) + '）');
      else seen.set(it.id, it.line);
    }
  }

  // 3. 顺序递增
  for (const pair of [['正文', body], ['索引表', idxRows]]) {
    const kind = pair[0];
    const list = pair[1];
    for (let k = 1; k < list.length; k++) {
      if (list[k].num < list[k - 1].num)
        fail(fileName, list[k].line, kind + '顺序错乱: ' + list[k].id + ' 出现在 ' + list[k - 1].id + ' 之后');
    }
  }

  // 4. 双向一致
  const bset = new Set(body.map((x) => x.id));
  const iset = new Set(idxRows.map((x) => x.id));
  for (const it of body) if (!iset.has(it.id)) fail(fileName, it.line, '正文有 ' + it.id + '，索引表未收录');
  for (const it of idxRows) if (!bset.has(it.id)) fail(fileName, it.line, '索引表有 ' + it.id + '，正文缺失');

  // 5. 跳号（warning）
  const max = body.reduce((a, x) => Math.max(a, x.num), 0);
  const nums = new Set(body.map((x) => x.num));
  for (let v = 1; v <= max; v++)
    if (!nums.has(v)) warn(fileName, 0, '编号跳号: 缺 ' + prefix + '-' + String(v).padStart(2, '0'));

  // 6. 六字段齐全
  body.forEach((it, k) => {
    const end = k + 1 < body.length ? body[k + 1].line - 1 : lines.length;
    const block = lines.slice(it.line, end).join('\n');
    const missing = FIELDS.filter((f) => !new RegExp('^[-*]\\s*' + f, 'm').test(block));
    if (missing.length) warn(fileName, it.line, it.id + ' 卡片缺字段: ' + missing.join('、'));
  });

  actualCounts[fileName] = body.length;
  fileStats.push({ file: fileName, count: body.length, chars: text.length });
}

function checkSkillMd() {
  const text = readNormalized(SKILL_FILE);

  // 7a. 领域文档索引的 “（N 条）”
  const reIdx = /^- \[references\/([\w-]+\.md)\]\(references\/[\w-]+\.md\) — [^（]*（(\d+)\s*条）/gm;
  let m;
  while ((m = reIdx.exec(text))) {
    const actual = actualCounts[m[1]];
    if (actual === undefined) {
      fail('SKILL.md', lineOf(text, m.index), '领域索引引用了未知文件: ' + m[1]);
      continue;
    }
    if (actual !== +m[2])
      fail('SKILL.md', lineOf(text, m.index), '计数漂移: ' + m[1] + ' 声明 ' + m[2] + ' 条，实际 ' + actual + ' 条');
  }

  // 领域文件必须在 SKILL.md 中被引用
  for (const f of Object.keys(PREFIX_BY_FILE)) {
    if (!text.includes('references/' + f)) fail('SKILL.md', 0, '领域文档索引遗漏: ' + f);
  }

  // 7b. 使用方式段落里的 “`x.md` (有) N 条”
  const reUsage = /`([\w-]+\.md)`\s*(?:有\s*)?(\d+)\s*条/g;
  while ((m = reUsage.exec(text))) {
    const actual = actualCounts[m[1]];
    if (actual !== undefined && actual !== +m[2])
      fail('SKILL.md', lineOf(text, m.index), '计数漂移: `' + m[1] + '` 声明 ' + m[2] + ' 条，实际 ' + actual + ' 条');
  }
}

function checkCrossRefs() {
  const targets = [SKILL_FILE].concat(fileStats.map((s) => path.join(REF_DIR, s.file)));
  for (const p of targets) {
    const text = readNormalized(p);
    const label = path.relative(ROOT, p).replace(/\\/g, '/');
    const re = /references\/([\w.-]+\.md)/g;
    let m;
    while ((m = re.exec(text))) {
      if (m[1] === path.basename(p)) continue; // 自引用跳过
      if (!fs.existsSync(path.join(REF_DIR, m[1])))
        fail(label, lineOf(text, m.index), '交叉引用不存在: references/' + m[1]);
    }
  }
}

// ---- main ----
const refFiles = fs
  .readdirSync(REF_DIR, { withFileTypes: true })
  .filter((d) => d.isFile() && d.name.endsWith('.md'))
  .map((d) => d.name)
  .sort();

for (const f of refFiles)
  if (!PREFIX_BY_FILE[f]) warn(f, 0, '未登记前缀映射（请更新 check.js 的 PREFIX_BY_FILE）');
for (const f of Object.keys(PREFIX_BY_FILE))
  if (!refFiles.includes(f)) warn('references/', 0, '映射中的文件不存在: ' + f);

for (const f of refFiles) checkRefFile(f);
checkSkillMd();
checkCrossRefs();

// ---- report ----
const total = fileStats.reduce((a, s) => a + s.count, 0);
const errors = problems.filter((p) => p.level === 'error');
const warns = problems.filter((p) => p.level === 'warn');

const badOf = (file) => errors.filter((e) => e.file === file).length;
const tag = (n) => (n ? '[ERR]' : '[OK ]');

console.log('dev-lessons check');
console.log('-'.repeat(56));
for (const s of fileStats) {
  console.log(tag(badOf(s.file)) + ' ' + s.file.padEnd(22) + String(s.count).padStart(3) + ' 条  ' + String(s.chars).padStart(6) + ' 字符' + (badOf(s.file) ? '   (' + badOf(s.file) + ' error)' : ''));
}
console.log(tag(badOf('SKILL.md')) + ' ' + 'SKILL.md'.padEnd(22) + '计数与交叉引用' + (badOf('SKILL.md') ? '   (' + badOf('SKILL.md') + ' error)' : ''));
console.log('-'.repeat(56));
console.log('领域文件 ' + fileStats.length + ' 个 / 条目 ' + total + ' 条 / error ' + errors.length + ' / warning ' + warns.length);

if (problems.length) {
  console.log('');
  problems
    .slice()
    .sort((a, b) => {
      const lv = (p) => (p.level === 'error' ? 0 : 1);
      return lv(a) - lv(b) || a.file.localeCompare(b.file) || a.line - b.line;
    })
    .forEach((p) => {
      const loc = p.line ? p.file + ':' + p.line : p.file;
      console.log((p.level === 'error' ? '[ERR] ' : '[WARN]') + ' ' + loc.padEnd(26) + p.msg);
    });
}

process.exitCode = errors.length ? 1 : 0;
