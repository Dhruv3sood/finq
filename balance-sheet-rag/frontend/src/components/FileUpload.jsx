import React, { useState } from 'react';
import { Upload, FileText } from 'lucide-react';

function FileUpload({ onUpload }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

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
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    // Check file type
    const allowedTypes = ['text/csv', 'text/plain', 'text/txt'];
    const fileExt = file.name.split('.').pop().toLowerCase();
    const allowedExts = ['csv', 'txt', 'text'];
    
    if (!allowedExts.includes(fileExt)) {
      alert('Please upload a CSV or TXT file');
      return;
    }
    
    setSelectedFile(file);
    onUpload(file);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Upload Balance Sheet</h2>
      
      <div
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-600 mb-2">
          Drag and drop your balance sheet file here, or
        </p>
        <label className="cursor-pointer">
          <span className="text-blue-600 hover:text-blue-700 font-medium">
            browse to upload
          </span>
          <input
            type="file"
            className="hidden"
            accept=".csv,.txt,.text"
            onChange={handleChange}
          />
        </label>
        <p className="text-sm text-gray-500 mt-4">
          Supported formats: CSV, TXT
        </p>
        {selectedFile && (
          <div className="mt-4 flex items-center justify-center gap-2 text-gray-700">
            <FileText className="h-5 w-5" />
            <span className="font-medium">{selectedFile.name}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default FileUpload;
