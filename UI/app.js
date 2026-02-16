const submitBtn = document.getElementById('submit');
const queryEl = document.getElementById('query');
const resultSection = document.getElementById('result');
const answerEl = document.getElementById('answer');
const sourcesEl = document.getElementById('sources');

const BACKEND = 'http://localhost:8000'; // change if backend runs elsewhere

submitBtn.addEventListener('click', async () => {
  const q = queryEl.value.trim();
  if (!q) return;
  submitBtn.disabled = true;
  answerEl.textContent = 'Thinking...';
  sourcesEl.textContent = '';
  resultSection.classList.remove('hidden');

  try {
    const resp = await fetch(`${BACKEND}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q }),
    });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    answerEl.textContent = data.answer ?? JSON.stringify(data);
    sourcesEl.textContent = (data.sources && data.sources.length) ? data.sources.join('\n') : 'No sources returned';
  } catch (err) {
    answerEl.textContent = 'Error: ' + err.message;
  } finally {
    submitBtn.disabled = false;
  }
});
