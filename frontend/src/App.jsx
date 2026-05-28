import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [servers, setServers] = useState([])
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [togglingServer, setTogglingServer] = useState({}) // keeps track of loading states by server name
  const [copiedText, setCopiedText] = useState({}) // keep track of which server IP was copied

  // Check connection status and fetch server list
  const checkConnectionAndFetchServers = async (isFirstLoad = false) => {
    if (isFirstLoad) {
      setLoading(true)
    }
    try {
      // Check health
      const healthRes = await fetch('/health')
      if (healthRes.ok) {
        setIsBackendConnected(true)
      } else {
        setIsBackendConnected(false)
      }

      // Fetch servers list
      const serversRes = await fetch('/api/servers/list')
      if (serversRes.ok) {
        const data = await serversRes.json()
        // If data is received, use it
        if (Array.isArray(data)) {
          setServers(data)
        } else if (data && typeof data === 'object' && !Array.isArray(data)) {
          // If a single object is returned
          setServers([data])
        } else {
          setServers([])
        }
        setError(null)
      } else {
        // If the server response is bad but backend is online, maybe portainer isn't configured.
        // We will show mock data for demonstration if no servers are found or it fails
        useFallbackMockData()
      }
    } catch (err) {
      setIsBackendConnected(false)
      // Fallback to mock data if backend is offline so the user can still see and edit the UI!
      useFallbackMockData()
    } finally {
      setLoading(false)
    }
  }

  const useFallbackMockData = () => {
    // Elegant fallback data for local frontend preview/editing
    setServers([
      { name: "survival-container", status: "running", ip_address: "192.168.1.100", port: 25565 },
      { name: "creative-container", status: "running", ip_address: "192.168.1.101", port: 25566 },
      { name: "skyblock-container", status: "stopped", ip_address: "192.168.1.102", port: 25567 }
    ])
    setError("Backend is currently offline or not configured. Displaying demo server cards for UI editing.")
  }

  useEffect(() => {
    checkConnectionAndFetchServers(true)
    
    // Polling interval to auto-refresh status every 15 seconds
    const interval = setInterval(() => {
      checkConnectionAndFetchServers(false)
    }, 15000)

    return () => clearInterval(interval)
  }, [])

  const handleToggle = async (serverName, currentStatus) => {
    setTogglingServer(prev => ({ ...prev, [serverName]: true }))
    
    try {
      // Optimistically handle mock data toggling if in demo mode
      if (!isBackendConnected) {
        await new Promise(resolve => setTimeout(resolve, 5000)) // simulate delay
        setServers(prev => prev.map(s => {
          if (s.name === serverName) {
            return {
              ...s,
              status: s.status === 'running' ? 'stopped' : 'running'
            }
          }
          return s
        }))
        setTogglingServer(prev => ({ ...prev, [serverName]: false }))
        return
      }

      // Real API Call
      const res = await fetch(`/api/servers/toggle/${serverName}`, {
        method: 'POST'
      })
      const result = await res.json()
      
      // Fetch latest server status after toggling
      await checkConnectionAndFetchServers(false)
    } catch (err) {
      console.error("Failed to toggle server state", err)
    } finally {
      setTogglingServer(prev => ({ ...prev, [serverName]: false }))
    }
  }

  const handleCopyIP = (serverName, ipAddress, port = 25565) => {
    const connectionString = `${ipAddress}:${port}`
    navigator.clipboard.writeText(connectionString)
    setCopiedText(prev => ({ ...prev, [serverName]: true }))
    setTimeout(() => {
      setCopiedText(prev => ({ ...prev, [serverName]: false }))
    }, 2000)
  }

  return (
    <div className="dashboard-container">
      {/* Header & Connection Status Bar */}
      <header className="dashboard-header">
        <div className="title-section">
          <div className="minecraft-logo-placeholder">⛏️</div>
          <h1>MC Server Control Panel</h1>
        </div>
        
        <div className={`connection-status ${isBackendConnected ? 'connected' : 'disconnected'}`}>
          <span className="pulse-dot"></span>
          <span className="status-text">
            {isBackendConnected ? 'API Connected (Online)' : 'API Disconnected (Offline / Demo Mode)'}
          </span>
        </div>
      </header>

      {/* Main Content Dashboard */}
      <main className="dashboard-main">
        {error && (
          <div className="demo-notice">
            <span className="notice-icon">⚠️</span>
            <p className="notice-text">{error}</p>
          </div>
        )}

        {loading && servers.length === 0 ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading Minecraft Servers...</p>
          </div>
        ) : (
          <div className="server-grid">
            {servers.map((server) => {
              const isRunning = server.status && server.status.toLowerCase().includes('running')
              const isToggling = togglingServer[server.name]
              const cleanName = server.name.replace('-container', '').replace('-', ' ')
              const port = server.port

              return (
                <div key={server.name} className={`server-card ${isRunning ? 'online' : 'offline'}`}>
                  {/* Card Header */}
                  <div className="card-header">
                    <h3 className="server-name">{cleanName}</h3>
                    <div className="status-badge-container">
                      <span className={`status-indicator-dot ${isRunning ? 'active' : 'inactive'}`}></span>
                      <span className="status-label">
                        {isRunning ? 'Online' : 'Offline'}
                      </span>
                    </div>
                  </div>

                  {/* Card Body with IP information */}
                  <div className="card-body">
                    <div className="info-row">
                      <span className="info-label">Address:</span>
                      <span className="info-value select-text">{server.ip_address}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Port:</span>
                      <span className="info-value">{port}</span>
                    </div>
                  </div>

                  {/* Card Footer with Controls */}
                  <div className="card-footer">
                    <button 
                      type="button" 
                      className={`copy-ip-btn ${copiedText[server.name] ? 'copied' : ''}`}
                      onClick={() => handleCopyIP(server.name, server.ip_address, port)}
                    >
                      {copiedText[server.name] ? (
                        <>
                          <span className="icon">✓</span> Copied!
                        </>
                      ) : (
                        <>
                          <span className="icon">📋</span> Copy IP
                        </>
                      )}
                    </button>

                    <button 
                      type="button" 
                      className={`power-toggle-btn ${isRunning ? 'stop-btn' : 'start-btn'}`}
                      disabled={isToggling}
                      onClick={() => handleToggle(server.name, server.status)}
                    >
                      {isToggling ? (
                        <>
                          <span className="spinner-small"></span> Updating...
                        </>
                      ) : isRunning ? (
                        <>
                          <span className="btn-icon">⏹</span> Stop Container
                        </>
                      ) : (
                        <>
                          <span className="btn-icon">▶</span> Start Container
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </main>

      <footer className="panel-footer">
        <p>Manage your Minecraft worlds seamlessly. Designed with ❤️ for Minecraft Server Admins.</p>
      </footer>
    </div>
  )
}

export default App
