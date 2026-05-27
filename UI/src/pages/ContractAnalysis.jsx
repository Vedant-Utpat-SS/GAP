import { useState, useEffect } from 'react';
import ChatWindow from '../components/Chat/ChatWindow';
import { fetchDocuments } from '../services/api';

const FileIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
);

const BrainIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-1.98-3A2.5 2.5 0 0 1 3 13.5a2.5 2.5 0 0 1 1.06-5A2.5 2.5 0 0 1 9.5 2Z"/>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 1.98-3A2.5 2.5 0 0 0 21 13.5a2.5 2.5 0 0 0-1.06-5A2.5 2.5 0 0 0 14.5 2Z"/>
  </svg>
);

export default function ContractAnalysis() {
  const [docs, setDocs]         = useState([]);
  const [activeDoc, setActiveDoc] = useState(null);
  const [search, setSearch]     = useState('');
  const [status, setStatus]     = useState('loading'); // 'loading' | 'ok' | 'error'

  useEffect(() => {
    fetchDocuments()
      .then(files => { setDocs(files); setStatus('ok'); })
      .catch(() => setStatus('error'));
  }, []);

  const filtered = docs.filter(d => d.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="ca-layout">
      {/* ── HEADER ── */}
      <header className="ca-header">
        <div className="ca-header-left">
          <div className="ca-logo-mark">
            <BrainIcon />
          </div>
          <span className="ca-brand-text">GAP</span>
          <span className="ca-sep">·</span>
          <span className="ca-page-label">Contract Analysis</span>
        </div>
        <div className="ca-header-right">
          <div className={`ca-status-badge ${status === 'ok' ? 'ok' : status === 'error' ? 'err' : 'loading'}`}>
            <span className="ca-dot">●</span>
            {status === 'loading' ? 'Connecting…' : status === 'ok' ? 'AI Ready' : 'Backend Offline'}
          </div>
          <div className="ca-user-av">AB</div>
        </div>
      </header>

      {/* ── BODY ── */}
      <div className="ca-body">
        {/* Sidebar */}
        <aside className="ca-sidebar">
          <div className="ca-sidebar-top">
            <div className="ca-title-row">
              <h2>
                <FileIcon />
                Documents
              </h2>
              <span className="ca-count-badge">{docs.length}</span>
            </div>
            <div className="ca-search-wrap">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input
                className="ca-search-inp"
                placeholder="Search documents…"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
          </div>

          <ul className="ca-doc-list">
            {status === 'loading' && (
              <li className="ca-doc-loading">Loading documents…</li>
            )}
            {status === 'error' && (
              <li className="ca-doc-loading" style={{ color: 'var(--error)' }}>
                Could not reach backend.
              </li>
            )}
            {status === 'ok' && filtered.length === 0 && (
              <li className="ca-doc-loading">No documents found.</li>
            )}
            {filtered.map(doc => (
              <li
                key={doc}
                className={`ca-doc-item ${activeDoc === doc ? 'active' : ''}`}
                onClick={() => setActiveDoc(activeDoc === doc ? null : doc)}
              >
                <div className="ca-doc-icon">📄</div>
                <div className="ca-doc-info">
                  <div className="ca-doc-name" title={doc}>{doc}</div>
                  <div className="ca-doc-meta">PDF · loaded</div>
                </div>
              </li>
            ))}
          </ul>
        </aside>

        {/* Main chat */}
        <main className="ca-main">
          {activeDoc && (
            <div className="ca-doc-banner">
              <FileIcon />
              Analysing: <span className="ca-doc-banner-name">{activeDoc}</span>
            </div>
          )}
          <ChatWindow activeDoc={activeDoc} />
        </main>
      </div>
    </div>
  );
}
