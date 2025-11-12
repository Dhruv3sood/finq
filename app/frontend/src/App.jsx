import React, { useState } from 'react';
import { MessageCircle, Presentation } from 'lucide-react';

// RAG Components
import RAGFileUpload from './components/rag/FileUpload';
import ProcessingStatus from './components/rag/ProcessingStatus';
import ChatInterface from './components/rag/ChatInterface';
import { uploadRAGFile } from './services/api';

// PPT Components
import PPTFileUpload from './components/ppt/FileUpload';
import ConfigurationPanel from './components/ppt/ConfigurationPanel';
import SlidePreview from './components/ppt/SlidePreview';
import DownloadButton from './components/ppt/DownloadButton';
import { generatePresentation } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('rag'); // 'rag' or 'ppt'

  // RAG State
  const [ragSessionId, setRagSessionId] = useState(null);
  const [ragSummaries, setRagSummaries] = useState([]);
  const [isProcessingRAG, setIsProcessingRAG] = useState(false);
  const [ragUploadStatus, setRagUploadStatus] = useState('idle');

  // PPT State
  const [pptSessionId, setPptSessionId] = useState(null);
  const [pptSlides, setPptSlides] = useState([]);
  const [pptTemplate, setPptTemplate] = useState('professional');
  const [pptTheme, setPptTheme] = useState('blue');
  const [generatingPPT, setGeneratingPPT] = useState(false);
  const [pptError, setPptError] = useState(null);

  // RAG Handlers
  const handleRAGFileUpload = async (balanceSheet, companyProfile) => {
    setIsProcessingRAG(true);
    setRagUploadStatus('processing');
    
    try {
      const data = await uploadRAGFile(balanceSheet, companyProfile);
      
      if (data.success) {
        setRagSessionId(data.session_id);
        setRagSummaries(data.summaries || []);
        setRagUploadStatus('success');
      } else {
        setRagUploadStatus('error');
        alert(data.error || 'Upload failed');
      }
    } catch (error) {
      setRagUploadStatus('error');
      alert('Error uploading file: ' + error.message);
    } finally {
      setIsProcessingRAG(false);
    }
  };

  const handleRAGReset = () => {
    setRagSessionId(null);
    setRagSummaries([]);
    setRagUploadStatus('idle');
    setIsProcessingRAG(false);
  };

  // PPT Handlers
  const handlePPTUploadSuccess = (sessionId) => {
    setPptSessionId(sessionId);
    setPptError(null);
  };

  const handlePPTGenerate = async (config) => {
    if (!pptSessionId) {
      setPptError('Please upload files first');
      return;
    }

    setGeneratingPPT(true);
    setPptError(null);

    try {
      const selectedSlides = config.slides || ['title', 'executive', 'financials', 'assets', 'liabilities', 'ratios', 'conclusion'];
      const result = await generatePresentation(pptSessionId, selectedSlides, config.template || pptTemplate, config.theme || pptTheme);
      if (result.success) {
        setPptSlides(result.slides);
      } else {
        setPptError(result.error || 'Generation failed');
      }
    } catch (err) {
      setPptError(err.message || 'Generation failed');
    } finally {
      setGeneratingPPT(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
          FinLore - Financial Analysis & Presentation
        </h1>
        
        {/* Tab Navigation */}
        <div className="flex justify-center mb-8 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('rag')}
            className={`px-6 py-3 font-semibold flex items-center gap-2 transition-colors ${
              activeTab === 'rag'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <MessageCircle className="h-5 w-5" />
            RAG Chat
          </button>
          <button
            onClick={() => setActiveTab('ppt')}
            className={`px-6 py-3 font-semibold flex items-center gap-2 transition-colors ${
              activeTab === 'ppt'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Presentation className="h-5 w-5" />
            PPT Generator
          </button>
        </div>

        {/* RAG Tab Content - Chatbot Interface */}
        {activeTab === 'rag' && (
          <div>
            {!ragSessionId ? (
              <div className="max-w-2xl mx-auto">
                <RAGFileUpload onUpload={handleRAGFileUpload} />
                {isProcessingRAG && <ProcessingStatus status={ragUploadStatus} />}
              </div>
            ) : (
              <div className="max-w-4xl mx-auto">
                <div className="mb-4 flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-gray-800">Chat with Your Financial Data</h2>
                  <button
                    onClick={handleRAGReset}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition text-sm"
                  >
                    Upload New Files
                  </button>
                </div>
                <ChatInterface sessionId={ragSessionId} />
              </div>
            )}
          </div>
        )}

        {/* PPT Tab Content */}
        {activeTab === 'ppt' && (
          <div>
            {!pptSessionId ? (
              <div className="max-w-2xl mx-auto">
                <PPTFileUpload onUploadSuccess={handlePPTUploadSuccess} />
              </div>
            ) : (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-1">
                    <ConfigurationPanel 
                      template={pptTemplate} 
                      theme={pptTheme}
                      onTemplateChange={setPptTemplate}
                      onThemeChange={setPptTheme}
                      onGenerate={handlePPTGenerate}
                      generating={generatingPPT}
                    />
                  </div>
                  <div className="lg:col-span-2 space-y-6">
                    {pptError && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                        {pptError}
                      </div>
                    )}
                    {pptSlides.length > 0 && <SlidePreview slides={pptSlides} />}
                    {pptSlides.length > 0 && <DownloadButton sessionId={pptSessionId} />}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

