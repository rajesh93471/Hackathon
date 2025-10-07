import React, { useState, useEffect, useRef, useCallback } from "react";
import "./App.css";
import { useSpeechRecognition } from './hooks/useSpeechRecognition';

function App() {
  const [command, setCommand] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [searchStats, setSearchStats] = useState({ total: 0, today: 0 });
  const [showSettings, setShowSettings] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [viewMode, setViewMode] = useState("grid");
  const [connectionStatus, setConnectionStatus] = useState("checking");
  const textareaRef = useRef(null);
  const resultsRef = useRef(null);
  
  const { text, isListening, startListening, isSpeechRecognitionSupported } = useSpeechRecognition();

  useEffect(() => {
    checkBackendConnection();
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    const savedHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
    const savedStats = JSON.parse(localStorage.getItem('searchStats') || '{"total": 0, "today": 0}');
    const savedViewMode = localStorage.getItem('viewMode') || 'grid';
    
    setDarkMode(savedDarkMode);
    setSearchHistory(savedHistory);
    setSearchStats(savedStats);
    setViewMode(savedViewMode);
  }, []);

  useEffect(() => { localStorage.setItem('darkMode', darkMode); }, [darkMode]);
  useEffect(() => { localStorage.setItem('searchHistory', JSON.stringify(searchHistory)); }, [searchHistory]);
  useEffect(() => { localStorage.setItem('searchStats', JSON.stringify(searchStats)); }, [searchStats]);
  useEffect(() => { localStorage.setItem('viewMode', viewMode); }, [viewMode]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [command]);

  useEffect(() => {
    if (results.length > 0 && resultsRef.current) {
      setTimeout(() => {
        resultsRef.current.scrollIntoView({ behavior: "smooth" });
      }, 300);
    }
  }, [results]);

  const checkBackendConnection = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/health", { method: "GET", headers: { "Content-Type": "application/json" } });
      setConnectionStatus(response.ok ? "connected" : "error");
    } catch (err) {
      setConnectionStatus("error");
      console.error("Backend connection failed:", err);
    }
  };

  const executeCommand = useCallback(async (cmd) => {
    const commandToExecute = (typeof cmd === 'string' ? cmd : command).trim();
    if (!commandToExecute) return;
    
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const startTime = Date.now();
      
      const response = await fetch("http://127.0.0.1:5000/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: commandToExecute }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const endTime = Date.now();
      const searchTime = ((endTime - startTime) / 1000).toFixed(1);

      if (data.error) {
        setError(data.error);
      } else {
        setResults(data.results || []);
        
        const newSearch = { query: commandToExecute, timestamp: new Date().toISOString(), resultsCount: data.results?.length || 0, searchTime: searchTime };
        
        setSearchHistory(prev => [newSearch, ...prev.slice(0, 9)]);
        setSearchStats(prev => ({ total: prev.total + 1, today: prev.today + 1 }));

        if (!data.results || data.results.length === 0) {
          setError("No results found. Please try a different search query.");
        }
      }
    } catch (err) {
      console.error("Search error:", err);
      setError(`Failed to fetch results: ${err.message}. Make sure the backend server is running on http://127.0.0.1:5000`);
    } finally {
      setLoading(false);
    }
  }, [command]);

  useEffect(() => {
    if (text) {
      setCommand(text);
    }
  }, [text]);

  useEffect(() => {
    if (!isListening && text) {
      executeCommand(text);
    }
  }, [isListening, text, executeCommand]);

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      executeCommand();
    }
  };

  const clearResults = () => { setResults([]); setError(null); };
  const toggleDarkMode = () => { setDarkMode(!darkMode); };
  const handleHistoryItemClick = (query) => {
    setCommand(query);
    setShowHistory(false);
    if (textareaRef.current) { textareaRef.current.focus(); }
  };
  const getUrl = (path, type) => {
    if (!path) return null;
    const filename = path.split("/").pop() || path.split("\\").pop();
    return `http://127.0.0.1:5000/${type}/${filename}`;
  };
  const filteredResults = results.filter(result => selectedFilter === "all" || result.category === selectedFilter);
  const availableCategories = [...new Set(results.map(r => r.category))].filter(Boolean);

  return (
    <div className={`app-container ${darkMode ? 'dark-mode' : ''}`}>
      <div className="animated-bg">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
          <div className="shape shape-4"></div>
        </div>
      </div>

      <nav className="navbar">
        <div className="nav-content">
          <div className="nav-brand">
            <div className="logo-icon">🚀</div>
            <span>Web Navigator AI</span>
            <div className={`connection-status ${connectionStatus}`}>
              <div className="status-dot"></div>
              <span className="status-text">
                {connectionStatus === "connected" ? "Connected" : 
                 connectionStatus === "error" ? "Backend Offline" : "Connecting..."}
              </span>
            </div>
          </div>
          <div className="nav-controls">
            <div className="search-stats">
              <span className="stat">
                <span className="stat-number">{searchStats.total}</span>
                <span className="stat-label">Total</span>
              </span>
              <span className="stat">
                <span className="stat-number">{searchStats.today}</span>
                <span className="stat-label">Today</span>
              </span>
            </div>
            <button className="nav-btn" onClick={() => setShowHistory(!showHistory)}>
              📊 History
            </button>
            <button className="nav-btn" onClick={() => setShowSettings(!showSettings)}>
              ⚙️ Settings
            </button>
            <button className="nav-btn theme-toggle" onClick={toggleDarkMode}>
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </nav>

      {showSettings && (
        <div className="settings-panel slide-down">
          <div className="settings-content">
            <h3>Settings</h3>
            <div className="setting-item">
              <label>View Mode:</label>
              <div className="view-toggle">
                <button 
                  className={viewMode === 'grid' ? 'active' : ''}
                  onClick={() => setViewMode('grid')}
                >
                  Grid
                </button>
                <button 
                  className={viewMode === 'list' ? 'active' : ''}
                  onClick={() => setViewMode('list')}
                >
                  List
                </button>
              </div>
            </div>
            <div className="setting-item">
              <label>Backend Status:</label>
              <div className={`connection-indicator ${connectionStatus}`}>
                {connectionStatus === "connected" ? "✅ Connected" : 
                 connectionStatus === "error" ? "❌ Disconnected" : "🔄 Checking..."}
              </div>
            </div>
            <button className="close-btn" onClick={() => setShowSettings(false)}>
              ✕ Close
            </button>
          </div>
        </div>
      )}

      {showHistory && (
        <div className="history-panel slide-down">
          <div className="history-content">
            <h3>Search History</h3>
            {searchHistory.length === 0 ? (
              <p className="no-history">No searches yet</p>
            ) : (
              <div className="history-list">
                {searchHistory.map((search, idx) => (
                  <div key={idx} className="history-item" onClick={() => handleHistoryItemClick(search.query)}>
                    <div className="history-query">{search.query}</div>
                    <div className="history-meta">
                      <span>{search.resultsCount} results</span>
                      <span>{search.searchTime}s</span>
                      <span>{new Date(search.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="history-actions">
              <button 
                className="clear-history-btn" 
                onClick={() => {
                  setSearchHistory([]);
                  setSearchStats({ total: 0, today: 0 });
                }}
              >
                🗑️ Clear History
              </button>
              <button className="close-btn" onClick={() => setShowHistory(false)}>
                ✕ Close
              </button>
            </div>
          </div>
        </div>
      )}

      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-title">
            <h1 className="gradient-text">Intelligent Web Navigation</h1>
            <div className="typing-animation">
              <p className="tagline">Navigate • Search • Discover • Analyze</p>
            </div>
          </div>
          
          <div className="search-container">
            <div className="search-box">
              <textarea
                ref={textareaRef}
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask me anything... e.g., 'Find the best laptops under 50k' or 'Search for trending AI tools'"
                className="search-input"
                disabled={loading}
              />
              <div className="search-actions">
                {command && (
                  <button className="clear-btn" onClick={() => setCommand("")}>
                    ✕
                  </button>
                )}
                
                {isSpeechRecognitionSupported && (
                  <button
                    type="button"
                    className={`voice-btn ${isListening ? 'listening' : ''}`}
                    onClick={startListening}
                    disabled={loading}
                    title="Search with your voice"
                  >
                    {isListening ? (
                      <div className="spinner-voice"></div>
                    ) : (
                      '🎤'
                    )}
                  </button>
                )}
                
                <button 
                  className="search-btn" 
                  onClick={() => executeCommand()} 
                  disabled={loading || !command.trim() || connectionStatus !== "connected"}
                >
                  {loading ? (
                    <div className="loading-spinner"><div className="spinner"></div></div>
                  ) : (
                    <><span>🔍</span><span>Search</span></>
                  )}
                </button>
              </div>
            </div>
            
            {error && (
              <div className="error-message fade-in">
                <span className="error-icon">⚠️</span>
                <span>{error}</span>
              </div>
            )}
          </div>

          <div className="quick-actions">
            <button className="quick-btn" onClick={() => setCommand("search for latest technology news")}>
              📱 Tech News
            </button>
            <button className="quick-btn" onClick={() => setCommand("find best restaurants near me")}>
              🍕 Restaurants
            </button>
            <button className="quick-btn" onClick={() => setCommand("compare smartphone prices")}>
              📊 Price Compare
            </button>
            <button className="quick-btn" onClick={() => setCommand("weather forecast today")}>
              🌤️ Weather
            </button>
          </div>
        </div>
      </section>

      {/* The Results Section now comes before the Features Section */}
      {results.length > 0 && (
        <section className="results-section fade-in" ref={resultsRef}>
          <div className="results-header">
            <div className="results-info">
              <h2>Search Results ({filteredResults.length})</h2>
              <p>Found {filteredResults.length} relevant results</p>
            </div>
            
            <div className="results-controls">
              <div className="filter-tabs">
                <button 
                  className={selectedFilter === 'all' ? 'active' : ''}
                  onClick={() => setSelectedFilter('all')}
                >
                  All
                </button>
                {availableCategories.map(category => (
                  <button 
                    key={category}
                    className={selectedFilter === category ? 'active' : ''}
                    onClick={() => setSelectedFilter(category)}
                  >
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </button>
                ))}
              </div>
              
              <button className="clear-results-btn" onClick={clearResults}>
                🗑️ Clear Results
              </button>
            </div>
          </div>

          <div className={`results-container ${viewMode}-view`}>
            {filteredResults.map((item, idx) => (
              <div key={idx} className="result-card stagger-animation" style={{ animationDelay: `${idx * 0.1}s` }}>
                <div className="result-header">
                  <div className="url-display">{new URL(item.link).hostname}</div>
                  <div className="result-category">{item.category}</div>
                  {item.status === 'success' && <div className="status-badge success">✓</div>}
                  {item.status === 'error' && <div className="status-badge error">✗</div>}
                </div>
                
                {item.thumbnail && (
                  <div className="screenshot-container">
                    <img
                      src={getUrl(item.thumbnail, 'thumbnail')}
                      alt="Website preview"
                      className="screenshot"
                      loading="lazy"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                    <div className="screenshot-overlay">
                      <a
                        href={getUrl(item.screenshot, 'screenshot')}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="preview-btn"
                      >
                        👁️ Full Screenshot
                      </a>
                    </div>
                  </div>
                )}
                
                <div className="result-content">
                  <a
                    href={item.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="result-title"
                  >
                    {item.title}
                  </a>
                  <p className="result-snippet">{item.content}</p>
                  
                  <div className="result-actions">
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="action-btn visit-btn"
                    >
                      <span>🔗</span>
                      <span>Visit</span>
                    </a>
                    <button 
                      className="action-btn"
                      onClick={(event) => {
                        navigator.clipboard.writeText(item.link);
                        const btn = event.target.closest('.action-btn');
                        const originalText = btn.innerHTML;
                        btn.innerHTML = '<span>✓</span><span>Copied!</span>';
                        setTimeout(() => {
                          btn.innerHTML = originalText;
                        }, 2000);
                      }}
                    >
                      <span>📋</span>
                      <span>Copy Link</span>
                    </button>
                    <button 
                      className="action-btn"
                      onClick={() => {
                        if (navigator.share) {
                          navigator.share({
                            title: item.title,
                            url: item.link
                          });
                        } else {
                          navigator.clipboard.writeText(`${item.title}\n${item.link}`);
                          alert('Link copied to clipboard!');
                        }
                      }}
                    >
                      <span>📤</span>
                      <span>Share</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* MOVED: The Features Section is now here, below the results area. */}
      <section className="features-section">
        <div className="features-header">
          <h2>Powerful AI-Driven Features</h2>
          <p>Experience the next generation of web navigation</p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card hover-lift">
            <div className="feature-icon">🧠</div>
            <h3>Smart AI Analysis</h3>
            <p>Advanced natural language processing to understand your queries and deliver precise results.</p>
            <div className="feature-badge">AI</div>
          </div>
          
          <div className="feature-card hover-lift">
            <div className="feature-icon">📸</div>
            <h3>Visual Previews</h3>
            <p>Instant screenshots and thumbnails help you preview content before clicking.</p>
          </div>
          
          <div className="feature-card hover-lift">
            <div className="feature-icon">⚡</div>
            <h3>Lightning Fast</h3>
            <p>Optimized for speed with intelligent caching and parallel processing.</p>
          </div>
          
          <div className="feature-card hover-lift">
            <div className="feature-icon">🎯</div>
            <h3>Precision Filtering</h3>
            <p>Advanced filters and categorization for targeted search results.</p>
          </div>
          
          <div className="feature-card hover-lift">
            <div className="feature-icon">📊</div>
            <h3>Analytics Dashboard</h3>
            <p>Track your search patterns and discover insights from your browsing habits.</p>
          </div>
          
          <div className="feature-card hover-lift">
            <div className="feature-icon">🔒</div>
            <h3>Privacy First</h3>
            <p>Your data stays local. No tracking, no data collection, complete privacy.</p>
          </div>
        </div>
      </section>

      {loading && (
        <div className="loading-section fade-in">
          <div className="loading-content">
            <div className="loading-animation">
              <div className="loading-dots">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
            <p>Searching the web intelligently...</p>
            <div className="loading-steps">
              <div className="step">🔍 Searching web...</div>
              <div className="step">📄 Extracting content...</div>
              <div className="step">📸 Taking screenshots...</div>
              <div className="step">🎯 Processing results...</div>
            </div>
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
          </div>
        </div>
      )}

      {connectionStatus === "error" && (
        <div className="connection-warning fade-in">
          <div className="warning-content">
            <h3>⚠️ Backend Connection Failed</h3>
            <p>Make sure the Python backend server is running:</p>
            <code>python main.py</code>
            <p>Server should be available at: <strong>http://127.0.0.1:5000</strong></p>
            <button className="retry-btn" onClick={checkBackendConnection}>
              🔄 Retry Connection
            </button>
          </div>
        </div>
      )}

      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>Web Navigator AI</h4>
            <p>Revolutionizing web search with artificial intelligence and visual previews</p>
            <div className="social-links">
              <a href="#" className="social-link">🐦</a>
              <a href="#" className="social-link">💼</a>
              <a href="#" className="social-link">📧</a>
            </div>
          </div>
          
          <div className="footer-section">
            <h4>Features</h4>
            <ul>
              <li>AI-Powered Search</li>
              <li>Visual Previews</li>
              <li>Smart Filtering</li>
              <li>Privacy Protection</li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Resources</h4>
            <ul>
              <li>API Documentation</li>
              <li>User Guide</li>
              <li>Support Center</li>
              <li>Feedback</li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Tech Stack</h4>
            <ul>
              <li>React Frontend</li>
              <li>Flask Backend</li>
              <li>Playwright Screenshots</li>
              <li>DuckDuckGo Search</li>
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2025 Web Navigator AI Agent. All rights reserved.</p>
          <p>Built with ❤️ using React, Flask & AI</p>
        </div>
      </footer>
    </div>
  );
}

export default App;