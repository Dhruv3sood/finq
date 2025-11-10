import React from 'react';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

function ProcessingStatus({ status }) {
  if (status === 'processing') {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-4">
        <div className="flex items-center gap-3">
          <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
          <div>
            <h3 className="font-semibold text-blue-900">Processing File</h3>
            <p className="text-sm text-blue-700">
              Analyzing balance sheet and generating summaries...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 mt-4">
        <div className="flex items-center gap-3">
          <CheckCircle className="h-6 w-6 text-green-600" />
          <div>
            <h3 className="font-semibold text-green-900">Upload Successful</h3>
            <p className="text-sm text-green-700">
              File processed successfully. You can now chat with your balance sheet data.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 mt-4">
        <div className="flex items-center gap-3">
          <XCircle className="h-6 w-6 text-red-600" />
          <div>
            <h3 className="font-semibold text-red-900">Upload Failed</h3>
            <p className="text-sm text-red-700">
              There was an error processing your file. Please try again.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default ProcessingStatus;
