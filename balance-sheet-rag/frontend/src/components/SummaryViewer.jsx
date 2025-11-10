import React from 'react';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';

function SummaryViewer({ summaries }) {
  const [expandedSections, setExpandedSections] = React.useState({});

  const toggleSection = (index) => {
    setExpandedSections(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  if (!summaries || summaries.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800">Summaries</h2>
        <p className="text-gray-500">No summaries available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold mb-4 text-gray-800 flex items-center gap-2">
        <FileText className="h-6 w-6" />
        Balance Sheet Summaries
      </h2>
      <div className="space-y-4">
        {summaries.map((summary, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg overflow-hidden"
          >
            <button
              onClick={() => toggleSection(index)}
              className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between transition-colors"
            >
              <span className="font-semibold text-gray-800">
                {summary.section || `Section ${index + 1}`}
              </span>
              {expandedSections[index] ? (
                <ChevronUp className="h-5 w-5 text-gray-600" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-600" />
              )}
            </button>
            {expandedSections[index] && (
              <div className="p-4 border-t border-gray-200">
                <div className="mb-3">
                  <h4 className="font-medium text-gray-700 mb-2">Summary:</h4>
                  <p className="text-gray-600 text-sm">{summary.summary}</p>
                </div>
                {summary.original_content && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <h4 className="font-medium text-gray-700 mb-2">Original Data:</h4>
                    <pre className="text-xs text-gray-600 whitespace-pre-wrap bg-gray-50 p-3 rounded">
                      {typeof summary.original_content === 'string' 
                        ? summary.original_content 
                        : JSON.stringify(summary.original_content, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default SummaryViewer;
