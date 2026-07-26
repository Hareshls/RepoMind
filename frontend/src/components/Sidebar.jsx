import React from 'react';
import { 
  Brain, 
  Plus, 
  Download, 
  Folder, 
  Rocket, 
  Trash2, 
  DownloadCloud, 
  Settings, 
  Crown,
  ChevronRight
} from 'lucide-react';

export default function Sidebar({ 
  repositories, 
  activeRepoUrl, 
  onSelectRepo, 
  onNewRepo, 
  onClearMemory, 
  onExportKnowledge, 
  onSettings 
}) {
  return (
    <aside style={{
      width: '280px',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 5,
      flexShrink: 0,
      padding: '16px 14px',
      gap: '20px',
      overflowY: 'auto',
      height: '100vh'
    }}>
      {/* Branding Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '4px 8px' }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '12px',
          background: 'var(--accent-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
          flexShrink: 0
        }}>
          <Brain size={24} />
        </div>
        <div>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2 }}>
            RepoMind
          </h1>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block' }}>
            AI Repository Intelligence
          </span>
        </div>
      </div>

      {/* REPOSITORIES Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 8px' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.8px' }}>
            REPOSITORIES
          </span>
          <button 
            onClick={onNewRepo}
            style={{
              background: 'rgba(139, 92, 246, 0.15)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              color: 'var(--accent-purple)',
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '3px 10px',
              borderRadius: '14px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Plus size={12} /> New
          </button>
        </div>

        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {repositories.map((repo) => {
            const isActive = activeRepoUrl === repo.url;
            return (
              <li 
                key={repo.url}
                onClick={() => onSelectRepo(repo.url)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  borderRadius: '12px',
                  background: isActive ? 'rgba(139, 92, 246, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${isActive ? 'rgba(139, 92, 246, 0.35)' : 'transparent'}`,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
                  <div style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '6px',
                    background: isActive ? 'rgba(139, 92, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: isActive ? 'var(--accent-purple)' : 'var(--text-secondary)',
                    flexShrink: 0
                  }}>
                    <Download size={15} />
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                    <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {repo.name}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {repo.sub || repo.name}
                    </span>
                  </div>
                </div>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: isActive ? 'var(--success-green)' : 'var(--text-muted)',
                  boxShadow: isActive ? '0 0 8px var(--success-green)' : 'none',
                  flexShrink: 0
                }} />
              </li>
            );
          })}
        </ul>

        <button 
          onClick={() => alert(`Indexed ${repositories.length} repositories in vector memory.`)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 12px',
            color: 'var(--text-secondary)',
            fontSize: '0.82rem',
            fontWeight: 500,
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            borderRadius: '8px'
          }}
        >
          <Folder size={16} /> View All Repositories
        </button>
      </div>

      {/* QUICK ACTIONS Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.8px', padding: '0 8px' }}>
          QUICK ACTIONS
        </span>

        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <li>
            <button 
              onClick={onNewRepo}
              style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '12px', color: 'var(--text-secondary)', fontSize: '0.88rem', fontWeight: 500, cursor: 'pointer', background: 'transparent', border: 'none', width: '100%', textAlign: 'left' }}
            >
              <Rocket size={18} color="var(--accent-cyan)" /> Analyze New Repository
            </button>
          </li>
          <li>
            <button 
              onClick={onClearMemory}
              style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '12px', color: 'var(--text-secondary)', fontSize: '0.88rem', fontWeight: 500, cursor: 'pointer', background: 'transparent', border: 'none', width: '100%', textAlign: 'left' }}
            >
              <Trash2 size={18} color="var(--error-red)" /> Clear Current Memory
            </button>
          </li>
          <li>
            <button 
              onClick={onExportKnowledge}
              style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '12px', color: 'var(--text-secondary)', fontSize: '0.88rem', fontWeight: 500, cursor: 'pointer', background: 'transparent', border: 'none', width: '100%', textAlign: 'left' }}
            >
              <DownloadCloud size={18} color="#38bdf8" /> Export Knowledge
            </button>
          </li>
          <li>
            <button 
              onClick={() => window.open(`http://127.0.0.1:8000/export/doc?repo_url=${encodeURIComponent(activeRepoUrl || '')}`, '_blank')}
              style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '12px', color: 'var(--text-secondary)', fontSize: '0.88rem', fontWeight: 500, cursor: 'pointer', background: 'transparent', border: 'none', width: '100%', textAlign: 'left' }}
            >
              <Download size={18} color="#3b82f6" /> Download Word (.docx)
            </button>
          </li>
          <li>
            <button 
              onClick={() => window.open(`http://127.0.0.1:8000/export/html?repo_url=${encodeURIComponent(activeRepoUrl || '')}`, '_blank')}
              style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '12px', color: 'var(--text-secondary)', fontSize: '0.88rem', fontWeight: 500, cursor: 'pointer', background: 'transparent', border: 'none', width: '100%', textAlign: 'left' }}
            >
              <Download size={18} color="#10b981" /> Download Report (.html)
            </button>
          </li>
          <li>
            <button 
              onClick={onSettings}
              style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '12px', color: 'var(--text-secondary)', fontSize: '0.88rem', fontWeight: 500, cursor: 'pointer', background: 'transparent', border: 'none', width: '100%', textAlign: 'left' }}
            >
              <Settings size={18} color="#94a3b8" /> Settings
            </button>
          </li>
        </ul>
      </div>

      {/* RepoMind Pro Banner */}
      <div style={{
        marginTop: 'auto',
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.1))',
        border: '1px solid rgba(139, 92, 246, 0.3)',
        borderRadius: '16px',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '0.95rem', color: 'white' }}>
          <Crown size={18} color="#f59e0b" /> RepoMind Pro
        </div>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
          Unlock advanced analytics, export, and more.
        </p>
        <button 
          onClick={() => alert('RepoMind Pro coming soon! Currently running 100% free open-source Hybrid AI Engine.')}
          style={{
            width: '100%',
            padding: '8px',
            background: 'rgba(139, 92, 246, 0.25)',
            border: '1px solid rgba(139, 92, 246, 0.4)',
            color: 'white',
            fontSize: '0.8rem',
            fontWeight: 600,
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          Coming Soon
        </button>
      </div>
    </aside>
  );
}
