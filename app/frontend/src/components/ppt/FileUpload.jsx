import React, { useState } from 'react';
import { Upload, FileText } from 'lucide-react';
import { uploadPPTFiles } from '../../services/api';

function PPTFileUpload({ onUploadSuccess }) {
  const [balanceSheet, setBalanceSheet] = useState(null);
  const [companyProfile, setCompanyProfile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleBalanceSheetChange = (e) => {
    setBalanceSheet(e.target.files[0]);
    setError(null);
  };

  const handleCompanyProfileChange = (e) => {
    setCompanyProfile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!balanceSheet) {
      setError('Please select a balance sheet file');
      return;
    }
    if (!companyProfile) {
      setError('Please select a company profile file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await uploadPPTFiles(balanceSheet, companyProfile);
      if (result.success) {
        onUploadSuccess(result.session_id);
      } else {
        setError(result.error || result.errors?.join(', ') || 'Upload failed');
      }
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Upload Documents</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Balance Sheet:
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
                accept=".txt,.csv,.xlsx,.pdf"
                onChange={handleBalanceSheetChange}
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
            Company Profile:
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
                accept=".txt,.csv,.xlsx,.pdf"
                onChange={handleCompanyProfileChange}
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
        disabled={uploading || !balanceSheet || !companyProfile}
        className="mt-6 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        {uploading ? 'Uploading...' : 'Upload Files'}
      </button>
      
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}

export default PPTFileUpload;

