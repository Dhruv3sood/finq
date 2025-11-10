import React, { useState } from 'react';
import { uploadFiles } from '../services/api';

function FileUpload({ onUploadSuccess }) {
  const [balanceSheet, setBalanceSheet] = useState(null);
  const [companyProfile, setCompanyProfile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

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
      const result = await uploadFiles(balanceSheet, companyProfile);
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
    <div className="file-upload">
      <h2>Upload Documents</h2>
      <div className="form-group">
        <label>Balance Sheet:</label>
        <input 
          type="file" 
          onChange={handleBalanceSheetChange} 
          accept=".txt,.csv,.xlsx"
        />
      </div>
      <div className="form-group">
        <label>Company Profile:</label>
      <input 
        type="file" 
          onChange={handleCompanyProfileChange} 
          accept=".txt,.csv,.xlsx"
      />
      </div>
      <button onClick={handleUpload} disabled={uploading || !balanceSheet || !companyProfile}>
        {uploading ? 'Uploading...' : 'Upload Files'}
      </button>
      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default FileUpload;

