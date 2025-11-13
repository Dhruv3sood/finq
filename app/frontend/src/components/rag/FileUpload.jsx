import React, { useState } from 'react';
import { Upload, FileText, Loader2, CheckCircle, Clock } from 'lucide-react';

function RAGFileUpload({ onUpload }) {
  const [balanceSheet, setBalanceSheet] = useState(null);
  const [companyProfile, setCompanyProfile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [processingComplete, setProcessingComplete] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleChange = (e, type) => {
    if (e.target.files && e.target.files[0]) {
      if (type === 'balance_sheet') {
        setBalanceSheet(e.target.files[0]);
      } else {
        setCompanyProfile(e.target.files[0]);
      }
    }
  };

  const handleFiles = (files) => {
    files.forEach(file => {
      const fileExt = file.name.split('.').pop().toLowerCase();
      const allowedExts = ['csv', 'txt', 'text', 'pdf'];
      
      if (allowedExts.includes(fileExt)) {
        if (!balanceSheet) {
          setBalanceSheet(file);
        } else if (!companyProfile) {
          setCompanyProfile(file);
        }
      }
    });
  };

  const handleUpload = async () => {
    if (!balanceSheet) {
      alert('Please upload a balance sheet file');
      return;
    }
    
    setIsProcessing(true);
    setProcessingComplete(false);
    setProcessingStatus('📤 Uploading files...');
    
    // Simulate upload progress
    setTimeout(() => setProcessingStatus('📄 Extracting text from documents...'), 500);
    setTimeout(() => setProcessingStatus('🧠 Parsing company profile with AI...'), 1500);
    setTimeout(() => setProcessingStatus('✂️ Splitting text into chunks...'), 3000);
    setTimeout(() => setProcessingStatus('🔢 Creating embeddings...'), 4500);
    setTimeout(() => setProcessingStatus('💾 Indexing in vector database...'), 6000);
    
    try {
    // Company profile is optional
      const result = await onUpload(balanceSheet, companyProfile);
      
      setProcessingStatus('✅ Ready for chatbot!');
      setProcessingComplete(true);
      
      // Show completion message
      setTimeout(() => {
        setIsProcessing(false);
      }, 2000);
    } catch (error) {
      setProcessingStatus('❌ Processing failed: ' + error.message);
      setTimeout(() => setIsProcessing(false), 3000);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Upload Documents</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Balance Sheet <span className="text-red-500">*</span>:
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
            <label className="cursor-pointer">
              <span className="text-blue-600 hover:text-blue-700 font-medium text-sm">
                {balanceSheet ? balanceSheet.name : 'Click to upload balance sheet'}
              </span>
              <input
                type="file"
                className="hidden"
                accept=".csv,.txt,.text,.pdf"
                onChange={(e) => handleChange(e, 'balance_sheet')}
              />
            </label>
            {balanceSheet && (
              <div className="mt-2 flex items-center justify-center gap-2 text-gray-700">
                <FileText className="h-4 w-4" />
                <span className="text-sm">{balanceSheet.name}</span>
              </div>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company Profile (Optional):
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
            <label className="cursor-pointer">
              <span className="text-blue-600 hover:text-blue-700 font-medium text-sm">
                {companyProfile ? companyProfile.name : 'Click to upload company profile'}
              </span>
              <input
                type="file"
                className="hidden"
                accept=".csv,.txt,.text,.pdf"
                onChange={(e) => handleChange(e, 'company_profile')}
              />
            </label>
            {companyProfile && (
              <div className="mt-2 flex items-center justify-center gap-2 text-gray-700">
                <FileText className="h-4 w-4" />
                <span className="text-sm">{companyProfile.name}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <button
        onClick={handleUpload}
        disabled={!balanceSheet || isProcessing}
        className="mt-6 w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center gap-2"
      >
        {isProcessing ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            Processing...
          </>
        ) : processingComplete ? (
          <>
            <CheckCircle className="h-5 w-5" />
            Uploaded Successfully
          </>
        ) : (
          <>
            <Upload className="h-5 w-5" />
        Upload & Process
          </>
        )}
      </button>

      {/* Processing Status */}
      {isProcessing && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Loader2 className="h-5 w-5 text-blue-600 animate-spin mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900 mb-1">
                {processingStatus}
              </p>
              <p className="text-xs text-blue-700">
                This usually takes 5-15 seconds depending on document size...
              </p>
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="mt-3 w-full bg-blue-200 rounded-full h-2 overflow-hidden">
            <div className="bg-blue-600 h-full rounded-full animate-pulse" 
                 style={{width: processingComplete ? '100%' : '60%', transition: 'width 0.5s ease-in-out'}}></div>
          </div>
        </div>
      )}

      {/* Success Message */}
      {processingComplete && !isProcessing && (
        <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-green-900">
                ✅ Documents processed successfully!
              </p>
              <p className="text-xs text-green-700 mt-1">
                Your chatbot is now ready. Start asking questions below! 💬
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default RAGFileUpload;
