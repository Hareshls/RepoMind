import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Analyzer from './components/Analyzer';
import Dashboard from './components/Dashboard';
import Chat from './components/Chat';
import { analyzeRepositoryAPI, askQuestionAPI, fetchRepositoriesAPI } from './services/api';

export default function App() {
  const [repositories, setRepositories] = useState([]);
  const [activeRepoUrl, setActiveRepoUrl] = useState('');
  const [repoData, setRepoData] = useState(null);
  const [archDescription, setArchDescription] = useState('');
  const [dependencies, setDependencies] = useState([]);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: "👋 Hello! I am RepoMind, your AI repository intelligence assistant. Enter a GitHub repository URL above or select an analyzed repository from the sidebar to begin!",
      citations: []
    }
  ]);
  const [isWaiting, setIsWaiting] = useState(false);
  const [isDarkTheme, setIsDarkTheme] = useState(true);

  // Load real repositories from backend vector memory on boot
  useEffect(() => {
    fetchRepositoriesAPI().then(res => {
      if (res && res.repositories && res.repositories.length > 0) {
        setRepositories(res.repositories);
        if (res.last_active) setActiveRepoUrl(res.last_active);
        else setActiveRepoUrl(res.repositories[0].url);
      } else {
        // Clear any old hardcoded mock data from localStorage if no repositories are in memory
        localStorage.removeItem('repomind_react_history');
      }
    });
  }, []);

  useEffect(() => {
    if (repositories.length > 0) {
      localStorage.setItem('repomind_react_history', JSON.stringify(repositories));
    }
  }, [repositories]);

  // Load repo metadata when switching active repo
  useEffect(() => {
    const found = repositories.find(r => r.url === activeRepoUrl);
    if (found) {
      setRepoData({
        repo: found.url,
        language: found.lang,
        framework: found.framework,
        entry_point: found.entry,
        files_analyzed: found.files
      });
    }
  }, [activeRepoUrl, repositories]);

  const handleAnalyze = async (url) => {
    setIsAnalyzing(true);
    setCurrentStep(0);

    // Animate timeline steps
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < 5) return prev + 1;
        return prev;
      });
    }, 600);

    try {
      const resData = await analyzeRepositoryAPI(url);
      clearInterval(interval);
      setCurrentStep(6);
      
      const name = url.split('/').filter(Boolean).pop().replace('.git', '');
      const parts = url.replace('https://github.com/', '').replace('.git', '').split('/');
      const sub = parts.length >= 2 ? `${parts[0]} / ${parts[1]}` : name;

      const newRepo = {
        url: url,
        name: name,
        sub: sub,
        lang: resData.language || 'Python',
        langPct: 'Indexed',
        framework: resData.framework || 'Standard Library / SDK',
        entry: resData.entry_point || 'README.md',
        files: resData.files_analyzed || '50'
      };

      setRepositories(prev => {
        const filtered = prev.filter(r => r.url !== url);
        return [newRepo, ...filtered];
      });
      setActiveRepoUrl(url);
      setRepoData(resData);
      
      // Auto-fetch dynamic summary
      fetchDynamicSummary(url);

    } catch (err) {
      clearInterval(interval);
      alert(`Analysis failed: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const fetchDynamicSummary = async (url) => {
    try {
      const res = await askQuestionAPI('What is the architecture and dependencies?', url);
      if (res.answer) {
        const parts = res.answer.split('\n\n');
        if (parts[0]) setArchDescription(parts[0].replace(/\*\*/g, ''));
        const depMatches = res.answer.match(/`([^`]+)`/g);
        if (depMatches && depMatches.length > 0) {
          const uniqueDeps = [...new Set(depMatches.map(d => d.replace(/`/g, '')))];
          setDependencies(uniqueDeps);
        }
      }
    } catch (e) {
      console.warn('Could not fetch dynamic summary.');
    }
  };

  const handleSendMessage = async (query) => {
    const userMsg = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMsg]);
    setIsWaiting(true);

    try {
      const res = await askQuestionAPI(query, activeRepoUrl);
      const aiMsg = {
        sender: 'ai',
        text: res.answer || 'No answer generated.',
        citations: res.sources || res.citations || []
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'ai',
        text: `⚠️ **Error**: ${err.message}`
      }]);
    } finally {
      setIsWaiting(false);
    }
  };

  const handleClearMemory = () => {
    if (confirm('Are you sure you want to clear repository history and vector memory?')) {
      setRepositories([]);
      setActiveRepoUrl('');
      setRepoData(null);
      setMessages([]);
    }
  };

  const handleExportKnowledge = () => {
    if (!activeRepoUrl) {
      alert('Please select a repository first.');
      return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(repoData || {}, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", "repomind_knowledge.json");
    dlAnchor.click();
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Background Glow Orbs */}
      <div className="app-background">
        <div className="glow-orb orb-1" />
        <div className="glow-orb orb-2" />
        <div className="glow-orb orb-3" />
      </div>

      {/* Left Sidebar */}
      <Sidebar 
        repositories={repositories}
        activeRepoUrl={activeRepoUrl}
        onSelectRepo={setActiveRepoUrl}
        onNewRepo={() => {
          const el = document.querySelector('input[placeholder*="github.com"]');
          if (el) el.focus();
        }}
        onClearMemory={handleClearMemory}
        onExportKnowledge={handleExportKnowledge}
        onSettings={() => alert('RepoMind Settings:\n\nActive Engine: Hybrid AI\nMax File Bytes: 100KB')}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, height: '100vh', overflow: 'hidden', zIndex: 2 }}>
        <Header 
          isDarkTheme={isDarkTheme}
          onToggleTheme={() => setIsDarkTheme(!isDarkTheme)}
          onToggleSidebar={() => {}}
        />

        {/* Scrollable Dashboard View */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <Analyzer 
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
            currentStep={currentStep}
          />

          <Dashboard 
            repoData={repoData}
            archDescription={archDescription}
            dependencies={dependencies}
          />

          <Chat 
            messages={messages}
            onSendMessage={handleSendMessage}
            onClearChat={() => setMessages([])}
            isWaiting={isWaiting}
          />
        </div>
      </main>
    </div>
  );
}
