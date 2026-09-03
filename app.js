import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

// SVG Icons
const Icons = {
  Mail: () => <svg className="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>,
  Lock: () => <svg className="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>,
  User: () => <svg className="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>,
  Eye: ({ visible, onClick }) => (
    <svg className="input-icon-right" onClick={onClick} style={{ opacity: visible ? 1 : 0.5, color: visible ? '#4ade80' : '#a0a0a0', cursor: 'none' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>
    </svg>
  ),
  Logo: () => <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/></svg>,
  LoginArrow: () => <svg style={{width: '18px', height: '18px'}} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
};

function App() {
  const [currentView, setCurrentView] = useState('login'); 
  const [authForm, setAuthForm] = useState({ fullName: '', email: '', password: '', confirmPassword: '' });
  const [authStatus, setAuthStatus] = useState('');
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [otpStep, setOtpStep] = useState(false);
  const [otpCode, setOtpCode] = useState('');

  // Main App View State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [documentData, setDocumentData] = useState(null);

  // Chatbot State
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hello! I am DIVA. Upload an identity document for forensic analysis, or ask me questions about forgery detection.' }
  ]);
  const chatEndRef = useRef(null);

  const cursorRef = useRef(null);
  const glassTiles = Array.from({ length: 40 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (cursorRef.current) {
        cursorRef.current.style.left = `${e.clientX}px`;
        cursorRef.current.style.top = `${e.clientY}px`;
      }
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isChatOpen]);

  const handleAuthChange = (e) => {
    setAuthForm({ ...authForm, [e.target.name]: e.target.value });
    setAuthStatus('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthStatus('Authenticating...');

    try {
      const response = await fetch(' https://diva-x9m9.onrender.com', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authForm.email, password: authForm.password }),
      });
      if (response.ok) {
        setCurrentView('app');
      } else {
        const err = await response.json();
        setAuthStatus(err.detail || 'Invalid credentials');
      }
    } catch (error) {
      setAuthStatus('Server connection failed. Is FastAPI running?');
    }
  };

  const handleRegisterFlow = async (e) => {
    e.preventDefault();
    if (!otpStep) {
      if (authForm.password !== authForm.confirmPassword) {
        return setAuthStatus('Passwords do not match!');
      }
      setAuthStatus(`Mock OTP sent to ${authForm.email}!`);
      setOtpStep(true);
      return;
    }

    if (otpCode !== "123456") return setAuthStatus('Invalid OTP. Please enter 123456.');
    
    setAuthStatus('Verifying OTP & creating account...');
    try {
      const response = await fetch(' https://diva-x9m9.onrender.com/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authForm.email, password: authForm.password }),
      });
      if (response.ok) {
        setAuthStatus('Account secured. Redirecting...');
        setTimeout(() => {
          setCurrentView('app');
          setOtpStep(false);
          setOtpCode('');
        }, 1000);
      } else {
        const err = await response.json();
        setAuthStatus(err.detail || 'Registration failed');
      }
    } catch (error) {
      setAuthStatus('Server connection failed.');
    }
  };

  const resetViews = (view) => {
    setCurrentView(view);
    setOtpStep(false);
    setOtpCode('');
    setAuthStatus('');
    setDocumentData(null);
    setIsChatOpen(false);
  };

  const handleUpload = async () => {
    if (!selectedFile) return setUploadStatus('Select a file first.');
    setIsAnalyzing(true);
    setUploadStatus('Scanning document layers...');
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(' https://diva-x9m9.onrender.com/upload/', {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        const data = await response.json();
        setDocumentData(data);
        setUploadStatus('');
      } else {
        setUploadStatus('Upload failed.');
      }
    } catch (error) {
      setUploadStatus('Backend disconnected.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = { role: 'user', text: chatInput };
    setMessages((prev) => [...prev, userMsg]);
    setChatInput('');

    try {
      const response = await fetch(' https://diva-x9m9.onrender.com/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMsg.text, 
          document_context: documentData 
        }),
      });
      
      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'bot', text: data.reply }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'bot', text: 'Error connecting to Ollama/FastAPI.' }]);
    }
  };

  return (
    <>
      {/* Background Ambience */}
      <div className="ambient-background">
        <div className="blob green"></div>
        <div className="blob lavender"></div>
        <div className="blob blue"></div>
      </div>
      <div className="glass-tile-grid">
        {glassTiles.map((_, i) => <div key={i} className="glass-tile"></div>)}
      </div>
      
      <div ref={cursorRef} className="cursor-light" />

      {/* Global Navigation */}
      <nav className="top-nav">
        <div className="nav-brand">
          <div className="nav-logo-box"><Icons.Logo /></div>
          <div className="nav-title">
            <span className="nav-title-main">DIVA</span>
            <span className="nav-title-sub">DIGITAL INTEGRATION & VIRTUAL ASSISTANT</span>
          </div>
        </div>
        <div className="nav-status-pill">
          <div className="status-dot"></div>
          SQLITE CONNECTED
        </div>
      </nav>

      {/* Authentication Views */}
      {currentView === 'login' && (
        <div className="auth-wrapper">
          <form className="auth-card" onSubmit={handleLogin}>
            <div className="auth-header">
              <div className="nav-logo-box"><Icons.Logo /></div>
              <h2 className="auth-title">DIVA PORTAL</h2>
              <p className="auth-subtitle">Enter your credentials</p>
            </div>
            <div className="input-group">
              <label className="input-label">Email Address <span>*</span></label>
              <div className="input-wrapper">
                <Icons.Mail />
                <input type="email" name="email" className="auth-input" onChange={handleAuthChange} required />
              </div>
            </div>
            <div className="input-group">
              <label className="input-label">Password <span>*</span></label>
              <div className="input-wrapper">
                <Icons.Lock />
                <input type={showPassword ? "text" : "password"} name="password" className="auth-input" onChange={handleAuthChange} required />
                <Icons.Eye visible={showPassword} onClick={() => setShowPassword(!showPassword)} />
              </div>
            </div>
            <button type="submit" className="auth-btn">
              <Icons.LoginArrow /> ACCESS PORTAL
            </button>
            {authStatus && <p style={{ color: '#ef4444', textAlign: 'center', marginTop: '1rem', fontSize: '0.8rem' }}>{authStatus}</p>}
            <div className="auth-footer">
              Don't have an account? <span style={{ cursor: 'none' }} onClick={() => resetViews('register')}>Create Account</span>
            </div>
          </form>
        </div>
      )}

      {currentView === 'register' && (
        <div className="auth-wrapper">
          <form className="auth-card" onSubmit={handleRegisterFlow}>
            <div className="auth-header">
              <h2 className="auth-title">CREATE ACCOUNT</h2>
              <p className="auth-subtitle">Direct database integration</p>
            </div>
            <div className="input-group" style={{ display: otpStep ? 'none' : 'flex' }}>
              <label className="input-label">Email Address <span>*</span></label>
              <div className="input-wrapper">
                <Icons.Mail />
                <input type="email" name="email" className="auth-input" onChange={handleAuthChange} required={!otpStep} />
              </div>
            </div>
            <div className="input-group" style={{ display: otpStep ? 'none' : 'flex' }}>
              <label className="input-label">Password <span>*</span></label>
              <div className="input-wrapper">
                <Icons.Lock />
                <input type={showPassword ? "text" : "password"} name="password" className="auth-input" onChange={handleAuthChange} required={!otpStep} />
                <Icons.Eye visible={showPassword} onClick={() => setShowPassword(!showPassword)} />
              </div>
            </div>
            <div className="input-group" style={{ display: otpStep ? 'none' : 'flex' }}>
              <label className="input-label">Confirm Password <span>*</span></label>
              <div className="input-wrapper">
                <Icons.Lock />
                <input type={showConfirmPassword ? "text" : "password"} name="confirmPassword" className="auth-input" onChange={handleAuthChange} required={!otpStep} />
                <Icons.Eye visible={showConfirmPassword} onClick={() => setShowConfirmPassword(!showConfirmPassword)} />
              </div>
            </div>
            {otpStep && (
              <div className="input-group">
                <label className="input-label" style={{ color: '#4ade80' }}>Enter Verification OTP <span>*</span></label>
                <div className="input-wrapper">
                  <Icons.Lock />
                  <input type="text" className="auth-input" placeholder="Hint: 123456" value={otpCode} onChange={(e) => setOtpCode(e.target.value)} required />
                </div>
              </div>
            )}
            <button type="submit" className="auth-btn">
               {!otpStep ? 'SEND VERIFICATION OTP' : 'VERIFY & REGISTER'}
            </button>
            {authStatus && <p style={{ color: otpStep ? '#4ade80' : '#ef4444', textAlign: 'center', marginTop: '1rem', fontSize: '0.8rem' }}>{authStatus}</p>}
            <div className="auth-footer">
              Already have an account? <span style={{ cursor: 'none' }} onClick={() => resetViews('login')}>Login here</span>
            </div>
          </form>
        </div>
      )}

      {/* Post-Login Work Area */}
      {currentView === 'app' && (
        <div className={`workspace-wrapper ${isChatOpen ? 'chat-active' : ''}`}>
          
          {/* Central Content Area (Shifts left when chat opens) */}
          <main className="main-content">
            {/* Header & Logout */}
            <div className="interactive-panel" style={{ marginBottom: '25px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h1 style={{ color: '#60a5fa', fontSize: '1.8rem', fontWeight: 800 }}>Document Verification</h1>
                <p style={{ color: '#a0a0a0', fontSize: '0.9rem', marginTop: '4px' }}>Upload government credentials for AI fraud analysis.</p>
              </div>
              <button className="logout-btn-header" onClick={() => resetViews('login')}>
                LOG OUT
              </button>
            </div>
            
            {/* Upload Section */}
            <div className="interactive-panel" style={{ display: 'flex', gap: '15px', alignItems: 'center', marginBottom: '25px' }}>
               <input type="file" onChange={(e) => setSelectedFile(e.target.files[0])} style={{ color: '#e0e0e0', flex: 1 }} />
               <button className="auth-btn" style={{ width: 'auto', padding: '12px 24px', borderRadius: '10px' }} onClick={handleUpload} disabled={isAnalyzing}>
                 {isAnalyzing ? 'Scanning...' : 'Analyze Document'}
               </button>
               {uploadStatus && <span style={{ color: '#a78bfa', fontSize: '0.9rem', fontWeight: 600 }}>{uploadStatus}</span>}
            </div>

            {/* Results Grid */}
            {documentData && (
               <div className="results-grid">
                  <div className="interactive-panel" style={{ textAlign: 'center' }}>
                     <h3 style={{ color: '#4ade80', fontSize: '1.1rem', marginBottom: '10px' }}>Risk Score</h3>
                     <div style={{ fontSize: '4.5rem', fontWeight: 800, color: documentData.risk_score > 50 ? '#ef4444' : '#4ade80', lineHeight: 1 }}>
                        {documentData.risk_score}
                     </div>
                     <span style={{ color: '#a0a0a0', fontSize: '0.9rem' }}>/ 100</span>
                  </div>
                  <div className="interactive-panel">
                     <h3 style={{ color: '#60a5fa', fontSize: '1.1rem', marginBottom: '12px' }}>AI Forensic Summary</h3>
                     <p style={{ color: '#e0e0e0', lineHeight: 1.6, fontSize: '0.95rem' }}>{documentData.explanation}</p>
                     
                     <h4 style={{ color: '#a78bfa', fontSize: '0.9rem', marginTop: '16px', marginBottom: '8px' }}>Detected Flags:</h4>
                     <ul style={{ paddingLeft: '20px', color: '#ef4444', fontSize: '0.85rem' }}>
                       {documentData.flags.length > 0 ? documentData.flags.map((f, i) => <li key={i}>{f}</li>) : <li style={{ color: '#4ade80' }}>Clean document profile</li>}
                     </ul>
                  </div>
               </div>
            )}
          </main>
          
          {/* Right Side Dock (Pinned) */}
          <aside className="right-dock">
            <div 
              className={`dock-logo ${isChatOpen ? 'active' : ''}`} 
              onClick={() => setIsChatOpen(!isChatOpen)}
              title="Toggle DIVA Chat"
            >
              D
            </div>
          </aside>

          {/* Sliding Chat Drawer */}
          <div className="chat-flyout">
            <h2 style={{ color: '#a78bfa', fontSize: '1.4rem' }}>DIVA Assistant</h2>
            <p style={{ color: '#a0a0a0', fontSize: '0.8rem', marginBottom: '20px', borderBottom: '1px solid rgba(167, 139, 250, 0.2)', paddingBottom: '16px' }}>
              Forensic Intelligence Chat
            </p>
            
            <div className="chat-messages">
              {messages.map((msg, i) => (
                <div key={i} className={`chat-bubble ${msg.role}`}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>

            <form onSubmit={handleChat} className="chat-input-container">
              <input 
                type="text" 
                placeholder="Ask about anomalies or document security..." 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button type="submit" className="auth-btn" style={{ width: 'auto', padding: '0 20px', borderRadius: '10px' }}>
                Send
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default App;