import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ProcessingStatus from './components/ProcessingStatus';
import SummaryViewer from './components/SummaryViewer';
import ChatInterface from './components/ChatInterface';
import { uploadFile } from './services/api';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [summaries, setSummaries] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, processing, success, error

  const handleFileUpload = async (file) => {
    setIsProcessing(true);
    setUploadStatus('processing');
    
    try {
      const data = await uploadFile(file);
      
      if (data.success) {
        setSessionId(data.session_id);
        setSummaries(data.summaries || []);
        setUploadStatus('success');
      } else {
        setUploadStatus('error');
        alert(data.error || 'Upload failed');
      }
    } catch (error) {
      setUploadStatus('error');
      alert('Error uploading file: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setSummaries([]);
    setUploadStatus('idle');
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
          Balance Sheet RAG
        </h1>
        
        {!sessionId ? (
          <div className="max-w-2xl mx-auto">
            <FileUpload onUpload={handleFileUpload} />
            {isProcessing && <ProcessingStatus status={uploadStatus} />}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <SummaryViewer summaries={summaries} />
              <button
                onClick={handleReset}
                className="w-full px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
              >
                Upload New File
              </button>
            </div>
            <div>
              <ChatInterface sessionId={sessionId} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
