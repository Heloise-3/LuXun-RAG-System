'use strict';
const form = document.getElementById('generate-form');
const query = document.getElementById('query');
const button = document.getElementById('generate-btn');
const statusBox = document.getElementById('status');
const errorBox = document.getElementById('error');
const output = document.getElementById('output');
const retrieval = document.getElementById('retrieval');
const metadata = document.getElementById('query-metadata');
let busy = false;
const count = () => { document.getElementById('count').textContent = `${query.value.length} / 1,000`; };
query.addEventListener('input', count);
document.querySelectorAll('[data-example]').forEach(item => item.addEventListener('click', () => {
  if (busy) return;
  query.value = item.dataset.example;
  count();
  query.focus();
}));
function paragraph(text, className) {
  const p = document.createElement('p');
  p.textContent = text;
  if (className) p.className = className;
  return p;
}
function resetResults() {
  output.replaceChildren();
  retrieval.replaceChildren();
  metadata.replaceChildren();
  document.getElementById('context').textContent = '';
  document.getElementById('context-panel').hidden = true;
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (busy) return;
  errorBox.hidden = true;
  if (!query.value.trim()) {
    errorBox.textContent = '请输入写作主题或待改写文字。';
    errorBox.hidden = false;
    return;
  }
  busy = true;
  button.disabled = true;
  button.textContent = '生成中…';
  query.readOnly = true;
  resetResults();
  output.setAttribute('aria-busy', 'true');
  statusBox.textContent = '正在分析主题、检索片段并生成文字…';
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 90000);
  try {
    const response = await fetch('/api/generate', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query: query.value.trim(), top_k: Number(document.getElementById('top-k').value)}),
      signal: controller.signal
    });
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : '输入无效，请检查字数后重试。');
    if (typeof data.output !== 'string' || !Array.isArray(data.retrieval) || !data.metadata) throw new Error('服务返回格式无效。');
    output.append(paragraph(data.output, 'generated-text'));
    const names = {tone: '语气', theme: '主题', device: '修辞', narrative: '叙事视角'};
    for (const [key, label] of Object.entries(names)) {
      const value = data.metadata[key];
      metadata.append(paragraph(`${label}：${Array.isArray(value) ? value.join(' / ') : value || '—'}`));
    }
    for (const result of data.retrieval) {
      const article = document.createElement('article');
      const title = document.createElement('h3');
      title.textContent = `${result.rank}. ${result.item.work || result.item.source} · 片段 ${result.item.id}`;
      article.append(title, paragraph(result.item.text, 'excerpt'));
      article.append(paragraph(`语义 ${result.semantic_score.toFixed(3)}　标签 ${result.metadata_score.toFixed(3)}　综合 ${result.final_score.toFixed(3)}`, 'scores'));
      article.append(paragraph(`标签：${[...result.item.tone, ...result.item.theme, ...result.item.device].join(' / ')} · ${result.item.narrative}`, 'tags'));
      article.append(paragraph(result.item.provenance_status === 'verified' ? `出处记录：${result.item.edition || ''} ${result.item.location || ''} ${result.item.source_url || ''}` : '出处待核验；请勿作为已核实引文。', 'source-note'));
      retrieval.append(article);
    }
    document.getElementById('context').textContent = data.context;
    document.getElementById('context-panel').hidden = false;
    statusBox.textContent = `完成。展示 ${data.retrieval.length} 段检索依据。`;
  } catch (error) {
    resetResults();
    errorBox.textContent = error.name === 'AbortError' ? '等待超时。请稍后重试；服务器可能仍在完成本次请求。' : (error instanceof TypeError ? '连接失败，请检查服务是否运行。' : error.message);
    errorBox.hidden = false;
    statusBox.textContent = '本次未生成结果。';
    output.append(paragraph('生成未完成。请查看左侧提示后重试。', 'empty'));
  } finally {
    clearTimeout(timeout);
    busy = false;
    button.disabled = false;
    button.textContent = '生成文字';
    query.readOnly = false;
    output.setAttribute('aria-busy', 'false');
  }
});
