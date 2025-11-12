import React, { useState } from 'react';
import { Upload, FileText } from 'lucide-react';

function RAGFileUpload({ onUpload }) {
  const [balanceSheet, setBalanceSheet] = useState(null);
  const [companyProfile, setCompanyProfile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

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

  const handleUpload = () => {
    if (!balanceSheet) {
      alert('Please upload a balance sheet file');
      return;
    }
    // Company profile is optional
    onUpload(balanceSheet, companyProfile);
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
        disabled={!balanceSheet}
        className="mt-6 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Upload & Process
      </button>
    </div>
  );
}

export default RAGFileUpload;
