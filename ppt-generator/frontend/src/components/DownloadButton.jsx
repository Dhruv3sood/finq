import React from 'react';
import { downloadPresentation } from '../services/api';

function DownloadButton({ sessionId }) {
  const handleDownload = async () => {
    if (!sessionId) {
      alert('No presentation available to download');
      return;
    }

    try {
      const blob = await downloadPresentation(sessionId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'presentation.pptx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert('Failed to download presentation: ' + error.message);
    }
  };

  if (!sessionId) {
    return null;
  }

  return (
    <div className="download-button">
      <button onClick={handleDownload} className="download-btn">
        Download PowerPoint
      </button>
    </div>
  );
}

export default DownloadButton;

