const BACKEND = 'http://localhost:8000'; // change if backend runs elsewhere

const submitBtn = document.getElementById('submit');
const queryEl = document.getElementById('query');
const resultSection = document.getElementById('result');
const answerEl = document.getElementById('answer');
const sourcesEl = document.getElementById('sources');

const uploadBtn = document.getElementById('uploadBtn');
const fileinput = document.getElementById('fileinput');
const refreshBtn = document.getElementById('refreshBtn');
const clearBtn = document.getElementById('clearBtn');
const filesList = document.getElementById('filesList');

const nameInput = document.getElementById('nameInput');
const emailInput = document.getElementById('emailInput');
const sendEmailBtn = document.getElementById('sendEmailBtn');
const emailStatus = document.getElementById('emailStatus');

async function listFiles() {
  try {
    const resp = await fetch(`${BACKEND}/files`);
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    filesList.innerHTML = data.files.map(f => `<div>${f}</div>`).join('') || '<div class="muted">No files</div>';
  } catch (err) {
    filesList.innerHTML = `<div class="muted">Error: ${err.message}</div>`;
  }
}

uploadBtn.addEventListener('click', async () => {
  const files = fileinput.files;
  if (!files || files.length === 0) return;
  uploadBtn.disabled = true;
  const form = new FormData();
  for (const f of files) form.append('files', f);

  try {
    const resp = await fetch(`${BACKEND}/upload`, { method: 'POST', body: form });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    alert('Saved: ' + (data.saved || []).join(', '));
    fileinput.value = null;
    await listFiles();
  } catch (err) {
    alert('Upload error: ' + err.message);
  } finally {
    uploadBtn.disabled = false;
  }
});

refreshBtn.addEventListener('click', async () => {
  try {
    refreshBtn.disabled = true;
    const resp = await fetch(`${BACKEND}/refresh`, { method: 'POST' });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    alert(data.status || 'Refresh started');
    await listFiles();
  } catch (err) {
    alert('Refresh error: ' + err.message);
  } finally {
    refreshBtn.disabled = false;
  }
});

clearBtn.addEventListener('click', async () => {
  if (!confirm('Delete uploaded files and clear DB?')) return;
  try {
    clearBtn.disabled = true;
    const resp = await fetch(`${BACKEND}/clear_db`, { method: 'POST' });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    alert('Removed: ' + (data.removed || []).join(', '));
    await listFiles();
  } catch (err) {
    alert('Clear error: ' + err.message);
  } finally {
    clearBtn.disabled = false;
  }
});

sendEmailBtn.addEventListener('click', async () => {
  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  if (!email) {
    emailStatus.textContent = 'Enter an email';
    return;
  }
  sendEmailBtn.disabled = true;
  emailStatus.textContent = 'Sending...';
  try {
    const resp = await fetch(`${BACKEND}/send_email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email })
    });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    emailStatus.textContent = data.status || 'scheduled';
  } catch (err) {
    emailStatus.textContent = 'Error: ' + err.message;
  } finally {
    sendEmailBtn.disabled = false;
  }
});

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

document.addEventListener('DOMContentLoaded', () => listFiles());
