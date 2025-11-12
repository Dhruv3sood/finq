import React from 'react';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

function ProcessingStatus({ status }) {
  if (status === 'processing') {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center gap-3">
        <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
        <p className="text-blue-800">Processing your balance sheet...</p>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
        <CheckCircle className="h-5 w-5 text-green-600" />
        <p className="text-green-800">File processed successfully!</p>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
        <XCircle className="h-5 w-5 text-red-600" />
        <p className="text-red-800">Error processing file</p>
      </div>
    );
  }

  return null;
}

export default ProcessingStatus;

