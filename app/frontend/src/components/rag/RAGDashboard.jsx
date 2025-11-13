import React, { useState } from 'react';
import { Upload, MessageCircle, FileText, CheckCircle, AlertCircle, Loader, RotateCcw, Clock } from 'lucide-react';
import FileUpload from './FileUpload';
import ChatInterface from './ChatInterface';
import ProcessingStatus from './ProcessingStatus';
import { uploadRAGFile } from '../../services/api';

function RAGDashboard({ onQueryComplete, onDocumentProcessed }) {
  const [sessionId, setSessionId] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  const [uploadStats, setUploadStats] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = async (balanceSheet, companyProfile) => {
    setUploadStatus('uploading');
    setError(null);
    
    try {
      const data = await uploadRAGFile(balanceSheet, companyProfile);
      
      if (data.success) {
        setSessionId(data.session_id);
        setUploadStats({
          chunks: data.chunks_count || 0,
          balanceSheetEntries: data.balance_sheet_entries || 0,
          companyProfileSections: data.company_profile_sections || 0,
          processingTime: data.processing_time || 0,
          readyForChat: data.ready_for_chat || false
        });
        setUploadStatus('success');
        if (onDocumentProcessed) onDocumentProcessed();
      } else {
        setUploadStatus('error');
        setError(data.error || 'Upload failed');
      }
      
      return data;
    } catch (err) {
      setUploadStatus('error');
      setError(err.message || 'Upload failed');
      throw err;
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setUploadStatus('idle');
    setUploadStats(null);
    setError(null);
  };

  if (!sessionId) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Upload className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Upload Documents</h2>
              <p className="text-sm text-gray-600">Upload your financial documents to start chatting</p>
            </div>
          </div>

          <FileUpload onUpload={handleFileUpload} />

          {uploadStatus === 'uploading' && (
            <div className="mt-6">
              <ProcessingStatus status={uploadStatus} />
            </div>
          )}

          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-semibold text-red-900">Upload Failed</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
            <div className="flex items-center space-x-3 mb-3">
              <MessageCircle className="h-6 w-6 text-blue-600" />
              <h3 className="font-bold text-blue-900">Intelligent Routing</h3>
            </div>
            <p className="text-sm text-blue-800">
              Queries are automatically routed based on type for optimal results
            </p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
            <div className="flex items-center space-x-3 mb-3">
              <CheckCircle className="h-6 w-6 text-purple-600" />
              <h3 className="font-bold text-purple-900">Grounding Validation</h3>
            </div>
            <p className="text-sm text-purple-800">
              All answers are validated against source documents to prevent hallucinations
            </p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
            <div className="flex items-center space-x-3 mb-3">
              <FileText className="h-6 w-6 text-green-600" />
              <h3 className="font-bold text-green-900">Source Citations</h3>
            </div>
            <p className="text-sm text-green-800">
              Every answer includes citations to original document sections
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
              <CheckCircle className="h-6 w-6" />
              Documents Processed Successfully - Chatbot Ready!
            </h3>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>{uploadStats?.chunks || 0} chunks indexed</span>
              </div>
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>{uploadStats?.balanceSheetEntries || 0} balance sheet entries</span>
              </div>
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>{uploadStats?.companyProfileSections || 0} profile sections</span>
              </div>
              {uploadStats?.processingTime && (
                <div className="flex items-center space-x-2 bg-white/20 px-3 py-1 rounded-full">
                  <Clock className="h-4 w-4" />
                  <span>Processed in {uploadStats.processingTime}s</span>
                </div>
              )}
            </div>
          </div>
          <button
            onClick={handleReset}
            className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition"
          >
            <RotateCcw className="h-4 w-4" />
            <span>Upload New</span>
          </button>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <ChatInterface 
          sessionId={sessionId} 
          onQueryComplete={onQueryComplete}
        />
      </div>
    </div>
  );
}

export default RAGDashboard;

