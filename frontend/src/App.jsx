import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState("");
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const API_URL = "https://cog-agent-backend.onrender.com/api";

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setReport(null);
      setJobId(null);
      setStatus(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) throw new Error("Upload failed");
      
      const data = await response.json();
      setJobId(data.job_id);
      setStatus("PROCESSING");
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let interval;
    if (jobId && (status === "PROCESSING" || status === "EXTRACTED")) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_URL}/status/${jobId}`);
          if (res.ok) {
            const data = await res.json();
            setStatus(data.status);
            setProgress(data.progress);
            
            if (data.status === "COMPLETED" || data.status === "FAILED") {
              clearInterval(interval);
              setIsLoading(false);
              
              if (data.status === "COMPLETED") {
                const reportRes = await fetch(`${API_URL}/report/${jobId}`);
                if (reportRes.ok) {
                  setReport(await reportRes.json());
                }
              }
            }
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [jobId, status]);

  // Calculate progress percentage
  let progressPct = 0;
  if (status === "EXTRACTED" && progress) {
    const [current, total] = progress.split("/").map(Number);
    if (total > 0) progressPct = (current / total) * 100;
  } else if (status === "COMPLETED") {
    progressPct = 100;
  }

  return (
    <div className="app-container animate-fade-in">
      <header>
        <h1>🕵️ Truth Layer</h1>
        <p className="subtitle">Automated Fact-Checking Agent. Upload a PDF document to extract claims and verify them against live web data.</p>
      </header>

      {!report && (
        <section className="glass-panel upload-section animate-fade-in">
          <h2>Upload Document</h2>
          <div className="file-input-wrapper">
            <label className="file-label">
              <input type="file" accept=".pdf" onChange={handleFileChange} />
              {file ? file.name : "Choose a PDF File"}
            </label>
          </div>
          <button 
            className="btn" 
            onClick={handleUpload} 
            disabled={!file || isLoading}
          >
            {isLoading ? "Processing..." : "Start Verification"}
          </button>

          {error && <p style={{color: 'var(--danger)', marginTop: '1rem'}}>{error}</p>}

          {status && (
            <div className="status-section">
              <p>Status: <strong>{status}</strong> {progress && `(${progress})`}</p>
              <div className="progress-bar-bg">
                <div className="progress-bar-fill" style={{ width: `${progressPct}%` }}></div>
              </div>
            </div>
          )}
        </section>
      )}

      {report && (
        <div className="animate-fade-in">
          <section className="glass-panel">
            <h2 style={{marginBottom: '1.5rem'}}>📊 Dashboard</h2>
            <div className="metrics-grid">
              <div className="metric-card">
                <h3>Total Claims</h3>
                <div className="metric-value">{report.total_claims}</div>
              </div>
              <div className="metric-card">
                <h3>Verified</h3>
                <div className="metric-value verified">{report.verified_count}</div>
              </div>
              <div className="metric-card">
                <h3>Inaccurate</h3>
                <div className="metric-value inaccurate">{report.inaccurate_count}</div>
              </div>
              <div className="metric-card">
                <h3>False</h3>
                <div className="metric-value false">{report.false_count}</div>
              </div>
            </div>
          </section>

          <section className="glass-panel">
            <h2 style={{marginBottom: '1.5rem'}}>📝 Extracted Claims</h2>
            {report.claims.map((claim, idx) => (
              <div key={idx} className={`claim-card ${claim.status.toLowerCase()}`}>
                <div className="claim-header">
                  <div className="claim-text">{claim.original_claim.claim_text}</div>
                  <span className={`badge ${claim.status.toLowerCase()}`}>{claim.status}</span>
                </div>
                <div style={{color: 'var(--text-secondary)', marginBottom: '1rem'}}>
                  <strong>Confidence:</strong> {claim.confidence_score} | <strong>Type:</strong> {claim.original_claim.claim_type}
                </div>
                {claim.correct_value && (
                  <div style={{color: 'var(--warning)', marginBottom: '0.5rem'}}>
                    <strong>Correct Value:</strong> {claim.correct_value}
                  </div>
                )}
                <p><strong>Explanation:</strong> {claim.explanation}</p>
                
                {claim.evidence_sources && claim.evidence_sources.length > 0 && (
                  <>
                    <h4 style={{marginTop: '1rem', color: 'var(--text-secondary)'}}>Evidence Sources</h4>
                    <ul className="evidence-list">
                      {claim.evidence_sources.map((ev, i) => (
                        <li key={i}>
                          <a href={ev.source_url} target="_blank" rel="noreferrer">{ev.source_title}</a>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            ))}
          </section>

          <div style={{textAlign: 'center', marginBottom: '2rem'}}>
            <button className="btn" onClick={() => {setReport(null); setFile(null); setJobId(null); setStatus(null);}}>
              Check Another Document
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
