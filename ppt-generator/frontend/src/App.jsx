import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ConfigurationPanel from './components/ConfigurationPanel';
import SlidePreview from './components/SlidePreview';
import DownloadButton from './components/DownloadButton';
import { generatePresentation } from './services/api';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [slides, setSlides] = useState([]);
  const [template, setTemplate] = useState('professional');
  const [theme, setTheme] = useState('blue');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async (config) => {
    if (!sessionId) {
      setError('Please upload files first');
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const selectedSlides = config.slides || ['title', 'executive', 'financials', 'assets', 'liabilities', 'ratios', 'conclusion'];
      const result = await generatePresentation(sessionId, selectedSlides, config.template || template, config.theme || theme);
      if (result.success) {
        setSlides(result.slides);
      } else {
        setError(result.error || 'Generation failed');
      }
    } catch (err) {
      setError(err.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="App">
      <h1>PPT Generator</h1>
      <FileUpload onUploadSuccess={setSessionId} />
      {sessionId && (
        <>
          <ConfigurationPanel 
            template={template} 
            theme={theme}
            onTemplateChange={setTemplate}
            onThemeChange={setTheme}
            onGenerate={handleGenerate}
            generating={generating}
          />
          {error && <div className="error">{error}</div>}
          {slides.length > 0 && <SlidePreview slides={slides} />}
          {slides.length > 0 && <DownloadButton sessionId={sessionId} />}
        </>
      )}
    </div>
  );
}

export default App;

