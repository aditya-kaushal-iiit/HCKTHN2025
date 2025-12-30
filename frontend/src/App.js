import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [user, setUser] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [tags, setTags] = useState('');
  const [context, setContext] = useState('');
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [uploadedReport, setUploadedReport] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [posting, setPosting] = useState(false);

  // Initialize or get user
  useEffect(() => {
    const initializeUser = async () => {
      try {
        const storedUserId = localStorage.getItem('userId');
        if (storedUserId) {
          const response = await axios.get(`${API_BASE_URL}/user/${storedUserId}`);
          if (response.data.success) {
            setUser(response.data.user);
            return;
          }
        }
        // Create new user
        const response = await axios.post(`${API_BASE_URL}/user/create`, {
          name: 'Civic Reporter',
          email: `user_${Date.now()}@civic.app`
        });
        if (response.data.success) {
          const newUser = response.data.user;
          localStorage.setItem('userId', newUser.id);
          setUser(newUser);
        }
      } catch (err) {
        console.error('Error initializing user:', err);
        setError('Failed to initialize. Please refresh the page.');
      }
    };
    initializeUser();
  }, []);

  // Fetch available platforms
  useEffect(() => {
    const fetchPlatforms = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/social/platforms`);
        if (response.data.success) {
          setPlatforms(response.data.platforms);
          setSelectedPlatforms(response.data.platforms); // Select all by default
        }
      } catch (err) {
        console.error('Error fetching platforms:', err);
      }
    };
    fetchPlatforms();
  }, []);

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
      setError(null);
      setResult(null);
      setAnalysis(null);
      setUploadedReport(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    if (!user) {
      setError('User not initialized. Please refresh the page.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedImage);
      formData.append('user_id', user.id);

      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setUploadedReport(response.data.report);
      } else {
        setError(response.data.error || 'Upload failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload image. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!uploadedReport) {
      setError('Please upload an image first');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        report_id: uploadedReport.id,
        image_url: uploadedReport.image_url,
        tags: tags,
        context: context
      });

      if (response.data.success) {
        setAnalysis(response.data.analysis);
      } else {
        setError(response.data.error || 'Analysis failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to analyze image. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGenerateCaption = async () => {
    if (!uploadedReport || !analysis) {
      setError('Please analyze the image first');
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/generate-caption`, {
        report_id: uploadedReport.id,
        image_url: uploadedReport.image_url,
        tags: tags,
        context: context,
        problem: analysis.problem
      });

      if (response.data.success) {
        setResult({
          id: uploadedReport.id,
          image_url: uploadedReport.image_url,
          category: analysis.problem,
          authority: analysis.authority,
          caption: response.data.caption,
          tags: tags
        });
        // Update user credits
        const userResponse = await axios.get(`${API_BASE_URL}/user/${user.id}`);
        if (userResponse.data.success) {
          setUser(userResponse.data.user);
        }
      } else {
        setError(response.data.error || 'Failed to generate caption');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate caption. Please try again.');
      console.error('Caption generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleMarkAsPosted = async () => {
    if (!result || !user) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/report/${result.id}/post`);
      if (response.data.success) {
        // Update user credits
        const userResponse = await axios.get(`${API_BASE_URL}/user/${user.id}`);
        if (userResponse.data.success) {
          setUser(userResponse.data.user);
        }
        alert('Post marked as shared! You earned 100 credits!');
      }
    } catch (err) {
      console.error('Error marking as posted:', err);
    }
  };

  const handlePostToSocial = async () => {
    if (!result || !user || selectedPlatforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    setPosting(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/report/${result.id}/post-to-social`, {
        platforms: selectedPlatforms
      });

      if (response.data.success) {
        // Update user credits
        const userResponse = await axios.get(`${API_BASE_URL}/user/${user.id}`);
        if (userResponse.data.success) {
          setUser(userResponse.data.user);
        }
        alert(`Successfully posted to ${selectedPlatforms.join(', ')}! You earned 100 credits!`);
      } else {
        setError(response.data.error || 'Failed to post to social media');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to post to social media. Please try again.');
      console.error('Error posting to social:', err);
    } finally {
      setPosting(false);
    }
  };

  const togglePlatform = (platform) => {
    setSelectedPlatforms(prev => 
      prev.includes(platform)
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  const handleReset = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setTags('');
    setContext('');
    setResult(null);
    setAnalysis(null);
    setUploadedReport(null);
    setError(null);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🏛️ Civic Reporter</h1>
          <p className="subtitle">AI-Powered Civic Issue Reporting</p>
          {user && (
            <div className="credits">
              <span className="credits-label">Credits:</span>
              <span className="credits-value">{user.credits}</span>
            </div>
          )}
        </header>

        {!result ? (
          <div className="upload-section">
            <div className="upload-area">
              {!imagePreview ? (
                <label htmlFor="image-upload" className="upload-label">
                  <div className="upload-icon">📷</div>
                  <p>Click to upload or drag and drop</p>
                  <p className="upload-hint">PNG, JPG, GIF up to 16MB</p>
                  <input
                    id="image-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleImageSelect}
                    className="file-input"
                  />
                </label>
              ) : (
                <div className="image-preview-container">
                  <img src={imagePreview} alt="Preview" className="image-preview" />
                  <button onClick={handleReset} className="change-image-btn">
                    Change Image
                  </button>
                </div>
              )}
            </div>

            {imagePreview && !uploadedReport && (
              <button
                onClick={handleUpload}
                disabled={loading}
                className="upload-btn"
              >
                {loading ? 'Uploading...' : 'Upload Image'}
              </button>
            )}

            {uploadedReport && (
              <>
                <div className="tags-section">
                  <label htmlFor="tags-input" className="tags-label">
                    Tags (optional):
                  </label>
                  <input
                    id="tags-input"
                    type="text"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="e.g., pothole, waste, water leak"
                    className="tags-input"
                  />
                </div>

                <div className="context-section">
                  <label htmlFor="context-input" className="tags-label">
                    Additional Context (optional):
                  </label>
                  <textarea
                    id="context-input"
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="Provide any additional details about the issue, location, urgency, etc."
                    className="context-input"
                    rows="4"
                  />
                </div>

                {!analysis ? (
                  <button
                    onClick={handleAnalyze}
                    disabled={analyzing}
                    className="analyze-btn"
                  >
                    {analyzing ? 'Analyzing...' : '🔍 Analyze Image'}
                  </button>
                ) : (
                  <>
                    <div className="analysis-results">
                      <h3 className="analysis-title">Analysis Results</h3>
                      <div className="detail-item">
                        <span className="detail-label">Issue Category:</span>
                        <span className="detail-value">{analysis.problem || 'N/A'}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Relevant Authorities:</span>
                        <span className="detail-value">{analysis.authority || 'N/A'}</span>
                      </div>
                    </div>

                    <button
                      onClick={handleGenerateCaption}
                      disabled={generating}
                      className="generate-caption-btn"
                    >
                      {generating ? 'Generating...' : '✨ Generate Social Media Post'}
                    </button>
                  </>
                )}
              </>
            )}

            {error && <div className="error-message">{error}</div>}
          </div>
        ) : (
          <div className="result-section">
            <div className="result-header">
              <h2>✨ Your Social Media Post is Ready!</h2>
              <button onClick={handleReset} className="new-post-btn">
                Create New Post
              </button>
            </div>

            <div className="result-content">
              <div className="result-image">
                <img src={result.image_url || uploadedReport?.image_url || imagePreview} alt="Report" />
              </div>

              <div className="result-details">
                <div className="detail-item">
                  <span className="detail-label">Issue Category:</span>
                  <span className="detail-value">{result.category || 'N/A'}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Relevant Authorities:</span>
                  <span className="detail-value">{result.authority || 'N/A'}</span>
                </div>

                <div className="social-post">
                  <div className="social-post-header">
                    <h3>📱 Social Media Caption</h3>
                    <button
                      onClick={() => copyToClipboard(result.caption)}
                      className="copy-btn"
                    >
                      Copy
                    </button>
                  </div>
                  <div className="social-post-content">
                    {result.caption || 'No caption generated'}
                  </div>
                </div>

                {result.tags && (
                  <div className="tags-display">
                    <span className="tags-label">Tags:</span>
                    <span className="tags-value">{result.tags}</span>
                  </div>
                )}

                <div className="platform-selection">
                  <h4 className="platform-title">Select Platforms to Post:</h4>
                  <div className="platform-checkboxes">
                    {platforms.length > 0 ? (
                      platforms.map(platform => (
                        <label key={platform} className="platform-checkbox">
                          <input
                            type="checkbox"
                            checked={selectedPlatforms.includes(platform)}
                            onChange={() => togglePlatform(platform)}
                          />
                          <span className="platform-name">{platform.charAt(0).toUpperCase() + platform.slice(1)}</span>
                        </label>
                      ))
                    ) : (
                      <p style={{ color: '#666', fontSize: '0.9rem' }}>Loading platforms...</p>
                    )}
                  </div>
                </div>

                {error && <div className="error-message">{error}</div>}

                <div className="action-buttons">
                  <button
                    onClick={handlePostToSocial}
                    disabled={posting || selectedPlatforms.length === 0}
                    className="post-to-social-btn"
                  >
                    {posting ? 'Posting...' : `🚀 Upload to Socials (+100 Credits)`}
                  </button>
                  <button
                    onClick={handleMarkAsPosted}
                    className="mark-posted-btn"
                  >
                    ✓ Mark as Posted Manually (+100 Credits)
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

