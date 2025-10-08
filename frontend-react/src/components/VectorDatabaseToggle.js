import React, { useState, useEffect } from 'react';

const VectorDatabaseToggle = () => {
  const [currentDb, setCurrentDb] = useState('');
  const [availableDbs, setAvailableDbs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [message, setMessage] = useState('');

  // Fetch current database status
  const fetchCurrentDatabase = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/vector-db/current');
      const data = await response.json();
      
      if (data.success) {
        setCurrentDb(data.current_database);
        setAvailableDbs(data.available_databases);
        setStatus(data.status);
        setMessage(data.message);
      } else {
        setMessage(data.message || 'Failed to fetch database info');
      }
    } catch (error) {
      console.error('Error fetching database info:', error);
      setMessage('Error connecting to backend');
    }
  };

  // Switch database
  const switchDatabase = async (newDbType) => {
    setIsLoading(true);
    setMessage('Switching database...');
    
    try {
      const formData = new FormData();
      formData.append('new_db_type', newDbType);
      
      const response = await fetch('http://localhost:8000/api/vector-db/switch', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (data.success) {
        setCurrentDb(data.current_database);
        setMessage(data.message);
        setStatus(data.status);
        
        // Show success message for a few seconds
        setTimeout(() => {
          setMessage('');
        }, 3000);
      } else {
        setMessage(data.message || 'Failed to switch database');
      }
    } catch (error) {
      console.error('Error switching database:', error);
      setMessage('Error switching database');
    } finally {
      setIsLoading(false);
    }
  };

  // Load initial data
  useEffect(() => {
    fetchCurrentDatabase();
  }, []);

  // Auto-refresh status every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchCurrentDatabase, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="vector-db-toggle-container">
      <div className="toggle-header">
        <h3 className="toggle-title">
          <span className="icon">🗄️</span>
          Vector Database
        </h3>
        <div className="status-indicator">
          <span className={`status-dot ${status === 'ready' ? 'ready' : 'not-ready'}`}></span>
          <span className="status-text">{status === 'ready' ? 'Ready' : 'Not Ready'}</span>
        </div>
      </div>

      <div className="current-database">
        <p className="current-label">Current Database:</p>
        <p className="current-value">{currentDb || 'Loading...'}</p>
      </div>

      <div className="database-options">
        {availableDbs.map((db) => (
          <button
            key={db}
            className={`db-option-btn ${currentDb === db.toUpperCase() ? 'active' : ''}`}
            onClick={() => switchDatabase(db)}
            disabled={isLoading || currentDb === db.toUpperCase()}
          >
            <span className="db-icon">
              {db === 'qdrant' ? '☁️' : '💾'}
            </span>
            <span className="db-name">{db.toUpperCase()}</span>
            {currentDb === db.toUpperCase() && <span className="active-indicator">✓</span>}
          </button>
        ))}
      </div>

      {message && (
        <div className={`message ${message.includes('Error') || message.includes('Failed') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {isLoading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <span>Switching database...</span>
        </div>
      )}

      <style jsx>{`
        .vector-db-toggle-container {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 12px;
          padding: 16px;
          margin: 16px 0;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
          transition: all 0.3s ease;
        }

        .vector-db-toggle-container:hover {
          transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
        }

        .toggle-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .toggle-title {
          margin: 0;
          color: #333;
          font-size: 1.2rem;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .icon {
          font-size: 1.4rem;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          transition: background-color 0.3s ease;
        }

        .status-dot.ready {
          background-color: #10b981;
          box-shadow: 0 0 6px rgba(16, 185, 129, 0.4);
        }

        .status-dot.not-ready {
          background-color: #ef4444;
          box-shadow: 0 0 6px rgba(239, 68, 68, 0.4);
        }

        .status-text {
          font-size: 0.85rem;
          color: #666;
          font-weight: 500;
        }

        .current-database {
          margin-bottom: 16px;
          padding: 12px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .current-label {
          margin: 0 0 4px 0;
          color: #666;
          font-size: 0.9rem;
          font-weight: 500;
        }

        .current-value {
          margin: 0;
          color: #333;
          font-size: 1.1rem;
          font-weight: 600;
        }

        .database-options {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
        }

        .db-option-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 12px 16px;
          border: 2px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
          color: #333;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
        }

        .db-option-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
          border-color: rgba(59, 130, 246, 0.3);
          transform: translateY(-1px);
        }

        .db-option-btn.active {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));
          border-color: rgba(16, 185, 129, 0.4);
          color: #059669;
        }

        .db-option-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .db-icon {
          font-size: 1.2rem;
        }

        .db-name {
          font-size: 0.9rem;
        }

        .active-indicator {
          position: absolute;
          top: -4px;
          right: -4px;
          background: #10b981;
          color: white;
          border-radius: 50%;
          width: 18px;
          height: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.7rem;
          font-weight: bold;
        }

        .message {
          padding: 10px 12px;
          border-radius: 6px;
          font-size: 0.9rem;
          font-weight: 500;
          margin-bottom: 12px;
          transition: all 0.3s ease;
        }

        .message.success {
          background: rgba(16, 185, 129, 0.1);
          border: 1px solid rgba(16, 185, 129, 0.2);
          color: #059669;
        }

        .message.error {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          color: #dc2626;
        }

        .loading-indicator {
          display: flex;
          align-items: center;
          gap: 10px;
          color: #666;
          font-size: 0.9rem;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(59, 130, 246, 0.2);
          border-top: 2px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 480px) {
          .database-options {
            flex-direction: column;
          }
          
          .toggle-header {
            flex-direction: column;
            gap: 8px;
            align-items: flex-start;
          }
        }
      `}</style>
    </div>
  );
};

export default VectorDatabaseToggle;