import React from 'react';
import { Download } from 'lucide-react';
import { downloadPresentation } from '../../services/api';

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
    <div className="bg-white rounded-lg shadow-md p-6">
      <button
        onClick={handleDownload}
        className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
      >
        <Download className="h-5 w-5" />
        Download PowerPoint
      </button>
    </div>
  );
}

export default DownloadButton;

