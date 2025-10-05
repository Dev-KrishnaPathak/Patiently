import React, { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './Dashboard.css'

const API_BASE_URL = 'http://localhost:8000/api'

export default function Dashboard() {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [activeTab, setActiveTab] = useState('upload') // upload, history, trends
  const [processingFile, setProcessingFile] = useState(null)
  const [selectedDocument, setSelectedDocument] = useState(null)
  const [documentAnalysis, setDocumentAnalysis] = useState(null)
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false)
  const [showResultsButton, setShowResultsButton] = useState(false)
  const fileInputRef = useRef(null)

  // Load documents from backend on mount
  useEffect(() => {
    loadDocuments()
  }, [])

  // Auto-load analysis when switching to trends tab
  useEffect(() => {
    if (activeTab === 'trends' && uploadedFiles.length > 0 && !documentAnalysis) {
      // Load the most recent document's analysis
      loadDocumentAnalysis(uploadedFiles[0].document_id)
    }
  }, [activeTab])

  // Load documents from backend
  const loadDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/documents`)
      if (response.ok) {
        const data = await response.json()
        const docs = data.documents || []
        setUploadedFiles(docs)
        // If we have documents and no selected one, select the most recent
        if (docs.length > 0 && !selectedDocument) {
          setSelectedDocument(docs[0].document_id)
          loadDocumentAnalysis(docs[0].document_id)
        }
      }
    } catch (error) {
      console.error('Failed to load documents:', error)
    }
  }

  // Load analysis for a specific document
  const loadDocumentAnalysis = async (documentId) => {
    setIsLoadingAnalysis(true)
    setSelectedDocument(documentId)
    console.log('Loading analysis for document:', documentId)
    try {
      const response = await fetch(`${API_BASE_URL}/document/${documentId}/analysis`)
      if (response.ok) {
        const analysis = await response.json()
        console.log('Analysis loaded:', analysis)
        console.log('Number of findings:', analysis.analysis?.findings?.length || 0)
        setDocumentAnalysis(analysis)
      } else {
        console.log('Analysis not ready, retrying in 2 seconds...')
        // Document might still be processing, retry after 2 seconds
        setTimeout(() => loadDocumentAnalysis(documentId), 2000)
      }
    } catch (error) {
      console.error('Failed to load analysis:', error)
      setTimeout(() => loadDocumentAnalysis(documentId), 2000)
    } finally {
      setIsLoadingAnalysis(false)
    }
  }

  // Delete a document
  const deleteDocument = async (documentId, e) => {
    e.stopPropagation() // Prevent card click event
    
    if (!confirm('Are you sure you want to delete this document?')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/document/${documentId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        // Remove from local state
        setUploadedFiles(prev => prev.filter(f => f.document_id !== documentId))
        
        // If this was the selected document, clear the analysis
        if (selectedDocument === documentId) {
          setSelectedDocument(null)
          setDocumentAnalysis(null)
        }
        
        // Show success message (you could add a toast notification here)
        console.log('Document deleted successfully')
      } else {
        console.error('Failed to delete document')
        alert('Failed to delete document. Please try again.')
      }
    } catch (error) {
      console.error('Delete error:', error)
      alert('Failed to delete document. Please try again.')
    }
  }

  // Handle file upload
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)
    processFiles(files)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    processFiles(files)
  }

  const processFiles = async (files) => {
    for (const file of files) {
      if (file.size <= 10 * 1024 * 1024) { // 10MB limit
        setProcessingFile(file.name)
        
        try {
          // Upload to backend
          const formData = new FormData()
          formData.append('file', file)
          
          const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
          })
          
          if (response.ok) {
            const result = await response.json()
            const documentId = result.document_id
            
            // Add to uploaded files list
            const newDoc = {
              id: documentId,
              filename: file.name,
              upload_date: new Date().toISOString(),
              status: 'processing'
            }
            setUploadedFiles(prev => [newDoc, ...prev])
            
            // Poll for analysis results
            setTimeout(() => {
              loadDocumentAnalysis(documentId)
              loadDocuments() // Refresh the list
            }, 3000)
            
            // Show the "View Results!" button
            setShowResultsButton(true)
            
            setProcessingFile(null)
          } else {
            console.error('Upload failed:', await response.text())
            setProcessingFile(null)
          }
        } catch (error) {
          console.error('Upload error:', error)
          setProcessingFile(null)
        }
      }
    }
  }

  // Mock data for trends
  const mockTrends = [
    { month: 'Apr', value: 200 },
    { month: 'Jun', value: 215 },
    { month: 'Aug', value: 205 },
    { month: 'Oct', value: 210 }
  ]

  return (
    <div className="db-container">
      {/* Header */}
      <header className="db-header">
        <Link to="/" className="db-back-link">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" />
          </svg>
          Back to Home
        </Link>
        <div className="db-header-center">Patiently</div>
        <div className="db-user-info">
          <div className="db-avatar">U</div>
          <span className="db-username">User</span>
        </div>
      </header>

      {/* Main Dashboard */}
      <main className="db-main">
        <div className="db-content-wrapper">
          
          {/* Welcome Section */}
          <div className="db-welcome animate-fadeIn">
            <h1 className="db-welcome-title">Welcome back!</h1>
            <p className="db-welcome-subtitle">Understanding your health, one document at a time</p>
          </div>

          {/* Tab Navigation */}
          <div className="db-tabs animate-slideUp" style={{animationDelay: '0.1s'}}>
            <button 
              className={`db-tab ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              Upload Document
            </button>
            <button 
              className={`db-tab ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9 22 9 12 15 12 15 22" />
              </svg>
              Document History
            </button>
            <button 
              className={`db-tab ${activeTab === 'trends' ? 'active' : ''}`}
              onClick={() => setActiveTab('trends')}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              Health Trends
            </button>
          </div>

          {/* Tab Content */}
          <div className="db-tab-content">
            
            {/* Upload Tab */}
            {activeTab === 'upload' && (
              <div className="db-upload-section animate-fadeIn">
                
                {/* View Results Button - Show at top when ready */}
                {showResultsButton && !processingFile && (
                  <div className="db-results-button-container animate-fadeIn">
                    <button 
                      className="db-btn-results"
                      onClick={() => {
                        setActiveTab('trends')
                        setShowResultsButton(false)
                      }}
                    >
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                      </svg>
                      View Results!
                    </button>
                    <p className="db-results-hint">Your document has been analyzed and results are ready</p>
                  </div>
                )}

                <div 
                  className={`db-dropzone ${isDragging ? 'dragging' : ''}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />
                  
                  <div className="db-dropzone-icon">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="17 8 12 3 7 8" />
                      <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                  </div>
                  
                  <h3 className="db-dropzone-title">
                    {isDragging ? 'Drop your files here' : 'Upload Medical Documents'}
                  </h3>
                  
                  <p className="db-dropzone-subtitle">
                    Drag and drop your files here, or click to browse
                  </p>
                  
                  <div className="db-dropzone-formats">
                    <span className="db-format-badge">PDF</span>
                    <span className="db-format-badge">JPG</span>
                    <span className="db-format-badge">PNG</span>
                  </div>
                  
                  <p className="db-dropzone-limit">Maximum file size: 10MB</p>
                </div>

                {processingFile && (
                  <div className="db-processing animate-pulse">
                    <div className="db-processing-spinner"></div>
                    <p>Analyzing {processingFile}...</p>
                  </div>
                )}

                {/* Supported Documents */}
                <div className="db-supported-docs">
                  <h3 className="db-section-title">Supported Documents</h3>
                  <div className="db-doc-types">
                    <div className="db-doc-type">
                      <span className="db-doc-icon">🩺</span>
                      <span>Lab Results</span>
                    </div>
                    <div className="db-doc-type">
                      <span className="db-doc-icon">🔬</span>
                      <span>Blood Work</span>
                    </div>
                    <div className="db-doc-type">
                      <span className="db-doc-icon">📊</span>
                      <span>Imaging Reports</span>
                    </div>
                    <div className="db-doc-type">
                      <span className="db-doc-icon">📋</span>
                      <span>Pathology Reports</span>
                    </div>
                    <div className="db-doc-type">
                      <span className="db-doc-icon">🏥</span>
                      <span>Discharge Summaries</span>
                    </div>
                    <div className="db-doc-type">
                      <span className="db-doc-icon">💊</span>
                      <span>Doctor's Notes</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
              <div className="db-history-section animate-fadeIn">
                <div className="db-section-header">
                  <h2 className="db-section-title">Document History</h2>
                  <p className="db-section-subtitle">View and manage all your uploaded documents</p>
                </div>

                {uploadedFiles.length === 0 ? (
                  <div className="db-empty-state">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                    <h3>No documents yet</h3>
                    <p>Upload your first medical document to get started</p>
                    <button className="db-btn-primary" onClick={() => setActiveTab('upload')}>
                      Upload Document
                    </button>
                  </div>
                ) : (
                  <div className="db-documents-list">
                    {uploadedFiles.map((file, index) => {
                      // Determine status emoji and text based on actual backend status
                      let statusEmoji = '⚪'
                      let statusText = 'Unknown'
                      
                      if (file.status === 'completed') {
                        statusEmoji = '🟢'
                        statusText = 'Processed'
                      } else if (file.status === 'processing') {
                        statusEmoji = '🟡'
                        statusText = 'Processing...'
                      } else if (file.status === 'failed') {
                        statusEmoji = '🔴'
                        statusText = 'Failed'
                      }
                      
                      return (
                      <div 
                        key={file.document_id} 
                        className="db-document-card animate-slideUp"
                        style={{animationDelay: `${index * 0.1}s`}}
                        onClick={() => {
                          if (file.status === 'completed') {
                            setActiveTab('trends')
                            loadDocumentAnalysis(file.document_id)
                          }
                        }}
                      >
                        <div className="db-doc-header">
                          <div className="db-doc-info">
                            <div className="db-doc-status" title={statusText}>{statusEmoji}</div>
                            <div>
                              <h4 className="db-doc-name">{file.filename}</h4>
                              <p className="db-doc-meta">
                                {statusText} • {file.document_type || 'Medical Document'} • {new Date(file.upload_time).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <div className="db-doc-actions">
                            <button 
                              className="db-doc-delete-btn" 
                              onClick={(e) => deleteDocument(file.document_id, e)}
                              title="Delete document"
                            >
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <polyline points="3 6 5 6 21 6" />
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                <line x1="10" y1="11" x2="10" y2="17" />
                                <line x1="14" y1="11" x2="14" y2="17" />
                              </svg>
                            </button>
                            <button className="db-doc-action">
                              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M9 18l6-6-6-6" />
                              </svg>
                            </button>
                          </div>
                        </div>
                        
                        <div className="db-doc-summary">
                          <p className="db-doc-summary-text">
                            {file.status === 'completed' ? 'Click to view detailed analysis' : 'Analysis in progress...'}
                          </p>
                        </div>
                      </div>
                    )})}
                  </div>
                )}
              </div>
            )}

            {/* Trends Tab */}
            {activeTab === 'trends' && (
              <div className="db-trends-section animate-fadeIn">
                <div className="db-section-header">
                  <h2 className="db-section-title">Health Trends & Lab Reports</h2>
                  <p className="db-section-subtitle">Track your health metrics over time and view detailed test results</p>
                </div>

                {uploadedFiles.length === 0 ? (
                  <div className="db-empty-state">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                    </svg>
                    <h3>No trends available</h3>
                    <p>Upload multiple documents to see your health trends</p>
                  </div>
                ) : (
                  <>
                  {/* Health Trends Charts */}
                  <div className="db-subsection">
                    <h3 className="db-subsection-title">📊 Test Results Overview</h3>
                    
                    {isLoadingAnalysis ? (
                      <div className="db-loading-state">
                        <div className="db-processing-spinner"></div>
                        <p>Loading analysis...</p>
                      </div>
                    ) : documentAnalysis && documentAnalysis.analysis && documentAnalysis.analysis.findings && documentAnalysis.analysis.findings.length > 0 ? (
                      <div className="db-bar-graph-container">
                        <div className="db-bar-graph-header">
                          <h4>Test Results by Status</h4>
                          <div className="db-bar-legend">
                            <span className="db-legend-item"><span className="db-legend-dot normal"></span> Normal</span>
                            <span className="db-legend-item"><span className="db-legend-dot warning"></span> Monitor</span>
                            <span className="db-legend-item"><span className="db-legend-dot critical"></span> Urgent</span>
                          </div>
                        </div>
                        
                        <div className="db-bar-graph">
                          {documentAnalysis.analysis.findings.map((finding, index) => {
                            const statusClass = finding.status === 'URGENT' ? 'critical' : 
                                              finding.status === 'MONITOR' ? 'warning' : 'normal'
                            
                            // Extract numeric value for bar height and display
                            let barHeight = 50 // default
                            let numericValue = ''
                            const valueStr = String(finding.value || '')
                            const numMatch = valueStr.match(/[\d.]+/)
                            if (numMatch) {
                              numericValue = numMatch[0]
                              const numValue = parseFloat(numericValue)
                              // Normalize to 0-100 range (this is simplified, real normalization would use ranges)
                              barHeight = Math.min(100, Math.max(10, numValue % 100))
                            }
                            
                            return (
                              <div key={index} className="db-bar-item" title={`${finding.test_name}: ${finding.value}`}>
                                <div className="db-bar-wrapper">
                                  <div 
                                    className={`db-bar ${statusClass}`} 
                                    style={{height: `${barHeight}%`}}
                                  >
                                    <span className="db-bar-value">{numericValue || finding.value}</span>
                                  </div>
                                </div>
                                <div className="db-bar-label">
                                  <span className="db-bar-test-name">{finding.test_name}</span>
                                  <span className={`db-bar-status ${statusClass}`}>
                                    {finding.status === 'URGENT' ? '🔴' : 
                                     finding.status === 'MONITOR' ? '🟡' : '🟢'}
                                  </span>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                        
                        {/* Summary Stats */}
                        <div className="db-bar-summary">
                          <div className="db-summary-stat normal">
                            <span className="db-summary-count">{documentAnalysis.analysis.normal_findings_count || 0}</span>
                            <span className="db-summary-label">Normal Tests</span>
                          </div>
                          <div className="db-summary-stat warning">
                            <span className="db-summary-count">{documentAnalysis.analysis.monitor_findings_count || 0}</span>
                            <span className="db-summary-label">Need Monitoring</span>
                          </div>
                          <div className="db-summary-stat critical">
                            <span className="db-summary-count">{documentAnalysis.analysis.urgent_findings_count || 0}</span>
                            <span className="db-summary-label">Urgent</span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="db-empty-state">
                        <p>No test results available for visualization</p>
                      </div>
                    )}
                    
                  </div>

                  {/* Detailed Lab Report Section */}
                  <div className="db-subsection" style={{marginTop: '2rem'}}>
                    <h3 className="db-subsection-title">📋 Detailed Lab Report</h3>
                    <p className="db-subsection-description">Complete breakdown of all test results from your latest lab work</p>
                    
                    {isLoadingAnalysis ? (
                      <div className="db-loading-state">
                        <div className="db-processing-spinner"></div>
                        <p>Loading analysis...</p>
                      </div>
                    ) : !documentAnalysis ? (
                      <div className="db-empty-state">
                        <p>No analysis available. Upload a document to see results.</p>
                      </div>
                    ) : (
                    <div className="db-lab-report-container">
                      {/* Report Header */}
                      <div className="db-lab-report-header">
                        <div className="db-lab-report-info">
                          <h4>{documentAnalysis.document_type || 'Medical Report'}</h4>
                          <p className="db-lab-report-date">
                            Report Date: {new Date(documentAnalysis.processed_at).toLocaleDateString()}
                          </p>
                        </div>
                        <button className="db-btn-outline-sm">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <polyline points="7 10 12 15 17 10" />
                            <line x1="12" y1="15" x2="12" y2="3" />
                          </svg>
                          Export PDF
                        </button>
                      </div>

                      {/* Overall Summary */}
                      <div className="db-overall-summary">
                        <h4>Overall Summary</h4>
                        <p>{documentAnalysis.analysis.overall_summary}</p>
                        <div className="db-overall-status">
                          <span className={`db-status-badge ${documentAnalysis.analysis.overall_status.toLowerCase()}`}>
                            {documentAnalysis.analysis.overall_status === 'URGENT' ? '🔴' : 
                             documentAnalysis.analysis.overall_status === 'MONITOR' ? '🟡' : '🟢'}
                            {' '}{documentAnalysis.analysis.overall_status}
                          </span>
                        </div>
                      </div>

                      {/* Test Results Grid - Dynamically shows ALL tests from the PDF */}
                      <div className="db-lab-tests-grid">
                        {documentAnalysis.analysis.findings && documentAnalysis.analysis.findings.length > 0 ? (
                          <>
                            {/* Show count of tests */}
                            <div className="db-test-count-banner">
                              <span>📋 Showing all {documentAnalysis.analysis.findings.length} test results from your report</span>
                            </div>
                            
                            {documentAnalysis.analysis.findings.map((finding, index) => {
                            const statusClass = finding.status === 'URGENT' ? 'critical' : 
                                              finding.status === 'MONITOR' ? 'warning' : 'normal'
                            const statusEmoji = finding.status === 'URGENT' ? '🔴' : 
                                              finding.status === 'MONITOR' ? '🟡' : '🟢'
                            
                            return (
                              <div key={index} className="db-lab-test-card">
                                <div className="db-test-header">
                                  <div className="db-test-name-with-info">
                                    <h5 className="db-test-name">{finding.test_name}</h5>
                                    {finding.what_it_means && (
                                      <div className="db-info-icon-wrapper">
                                        <span className="db-info-icon">ℹ️</span>
                                        <div className="db-info-tooltip">
                                          {finding.what_it_means}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                  <span className={`db-test-status ${statusClass}`}>
                                    {statusEmoji} {finding.status}
                                  </span>
                                </div>
                                <div className="db-test-values">
                                  <div className="db-test-value-main">
                                    <span className="db-value-number">{finding.value}</span>
                                  </div>
                                  <div className="db-test-range">
                                    Normal Range: {finding.normal_range}
                                  </div>
                                </div>
                                <p className="db-test-explanation">
                                  <strong>What this means:</strong> {finding.plain_english}
                                </p>
                                {finding.what_it_means && (
                                  <p className="db-test-context">
                                    <strong>Context:</strong> {finding.what_it_means}
                                  </p>
                                )}
                                {finding.clinical_significance && (
                                  <p className="db-test-significance">
                                    <strong>Clinical Significance:</strong> {finding.clinical_significance}
                                  </p>
                                )}
                                {finding.recommendations && finding.recommendations.length > 0 && (
                                  <div className="db-test-recommendations">
                                    <strong>Recommendations:</strong>
                                    <ul>
                                      {finding.recommendations.map((rec, i) => (
                                        <li key={i}>{rec}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            )
                          })}
                          </>
                        ) : (
                          <p>No test findings available</p>
                        )}
                      </div>

                      {/* Summary Footer */}
                      <div className="db-lab-report-summary">
                        <div className="db-summary-stats">
                          <div className="db-summary-stat">
                            <span className="db-summary-icon">📊</span>
                            <div>
                              <div className="db-summary-number">
                                {documentAnalysis.analysis.findings?.length || 0}
                              </div>
                              <div className="db-summary-label">Total Tests</div>
                            </div>
                          </div>
                          <div className="db-summary-stat">
                            <span className="db-summary-icon">🟢</span>
                            <div>
                              <div className="db-summary-number">
                                {documentAnalysis.analysis.normal_findings_count || 0}
                              </div>
                              <div className="db-summary-label">Normal</div>
                            </div>
                          </div>
                          <div className="db-summary-stat">
                            <span className="db-summary-icon">🟡</span>
                            <div>
                              <div className="db-summary-number">
                                {documentAnalysis.analysis.monitor_findings_count || 0}
                              </div>
                              <div className="db-summary-label">Need Monitoring</div>
                            </div>
                          </div>
                          <div className="db-summary-stat">
                            <span className="db-summary-icon">🔴</span>
                            <div>
                              <div className="db-summary-number">
                                {documentAnalysis.analysis.urgent_findings_count || 0}
                              </div>
                              <div className="db-summary-label">Need Attention</div>
                            </div>
                          </div>
                        </div>
                        
                        {/* Questions Section */}
                        {documentAnalysis.questions && documentAnalysis.questions.length > 0 && (
                          <div className="db-questions-section">
                            <h4>💬 Questions for Your Doctor</h4>
                            <div className="db-questions-list">
                              {documentAnalysis.questions.map((q, i) => (
                                <div key={i} className="db-question-card">
                                  <span className={`db-question-priority ${q.priority.toLowerCase()}`}>
                                    {q.priority}
                                  </span>
                                  <p>{q.question}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div className="db-summary-actions">
                          <button className="db-btn-primary">
                            Schedule Doctor Visit
                          </button>
                          <button className="db-btn-outline">
                            Download Full Report
                          </button>
                        </div>
                      </div>
                    </div>
                    )}
                  </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="db-quick-actions animate-slideUp" style={{animationDelay: '0.2s'}}>
            <h3 className="db-section-title">Quick Actions</h3>
            <div className="db-action-grid">
              <button className="db-action-btn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                <span>Ask Questions</span>
              </button>
              <button className="db-action-btn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
                <span>Export Report</span>
              </button>
              <button className="db-action-btn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                <span>Share with Doctor</span>
              </button>
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="db-privacy-notice animate-fadeIn" style={{animationDelay: '0.3s'}}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            <p>
              <strong>Your privacy matters.</strong> All documents are encrypted and automatically deleted after 7 days. 
              We never share your data with third parties.
            </p>
          </div>

        </div>
      </main>
    </div>
  )
}
