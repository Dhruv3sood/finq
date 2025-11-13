import React, { useState } from 'react';
import { 
  Upload, 
  Presentation, 
  CheckCircle, 
  AlertCircle, 
  RotateCcw,
  Sparkles,
  Download,
  Eye
} from 'lucide-react';
import FileUpload from './FileUpload';
import ConfigurationPanel from './ConfigurationPanel';
import SlidePreview from './SlidePreview';
import DownloadButton from './DownloadButton';

function PPTDashboard({ onPPTGenerated, onDocumentProcessed }) {
  const [sessionId, setSessionId] = useState(null);
  const [slides, setSlides] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [metadata, setMetadata] = useState(null);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  const handleUploadSuccess = (uploadedSessionId) => {
    setSessionId(uploadedSessionId);
    setError(null);
    if (onDocumentProcessed) onDocumentProcessed();
    
    // Fetch recommendations
    fetchRecommendations(uploadedSessionId);
  };

  const fetchRecommendations = async (sid) => {
    try {
      const response = await fetch(`http://localhost:5000/api/ppt/recommendations/${sid}`);
      const data = await response.json();
      if (data.success) {
        setRecommendations(data.recommended_slides);
      }
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
    }
  };

  const handleGenerate = async (config) => {
    setGenerating(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/ppt/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          slides: config.slides,
          template: config.template,
          theme: config.theme,
          use_agentic: true
        })
      });

      const data = await response.json();

      if (data.success) {
        setSlides(data.slides);
        setMetadata(data.metadata);
        if (onPPTGenerated) onPPTGenerated();
      } else {
        setError(data.error || 'Generation failed');
      }
    } catch (err) {
      setError(err.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setSlides([]);
    setMetadata(null);
    setError(null);
    setRecommendations(null);
  };

  if (!sessionId) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-purple-100 p-3 rounded-lg">
              <Upload className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Upload Documents</h2>
              <p className="text-sm text-gray-600">Upload balance sheet and company profile to generate presentations</p>
            </div>
          </div>

          <FileUpload onUploadSuccess={handleUploadSuccess} />

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

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
            <div className="flex items-center space-x-3 mb-3">
              <Sparkles className="h-6 w-6 text-purple-600" />
              <h3 className="font-bold text-purple-900">AI-Powered</h3>
            </div>
            <p className="text-sm text-purple-800">
              Automated slide generation with intelligent content structuring
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
            <div className="flex items-center space-x-3 mb-3">
              <CheckCircle className="h-6 w-6 text-blue-600" />
              <h3 className="font-bold text-blue-900">Quality Assured</h3>
            </div>
            <p className="text-sm text-blue-800">
              Every slide is validated and scored for quality (0-100)
            </p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
            <div className="flex items-center space-x-3 mb-3">
              <Presentation className="h-6 w-6 text-green-600" />
              <h3 className="font-bold text-green-900">Professional</h3>
            </div>
            <p className="text-sm text-green-800">
              Multiple templates and themes for polished presentations
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-500 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold mb-2">Ready to Generate Presentation</h3>
            <p className="text-sm text-purple-100">
              Configure your presentation settings and generate professional slides
            </p>
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

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
          <div>
            <p className="font-semibold text-red-900">Generation Failed</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1">
          <ConfigurationPanel
            generating={generating}
            onGenerate={handleGenerate}
            recommendations={recommendations}
          />
        </div>

        {/* Preview and Results */}
        <div className="lg:col-span-2 space-y-6">
          {generating && (
            <div className="bg-white rounded-xl p-12 text-center border border-gray-200 shadow-lg">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
                <Sparkles className="h-8 w-8 text-purple-600 animate-pulse" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Generating Presentation</h3>
              <p className="text-sm text-gray-600">
                AI is creating your professional slides with quality checks...
              </p>
            </div>
          )}

          {!generating && slides.length === 0 && (
            <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                <Presentation className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Presentation Yet</h3>
              <p className="text-sm text-gray-600">
                Configure your settings and click "Generate Presentation" to get started
              </p>
            </div>
          )}

          {!generating && slides.length > 0 && (
            <>
              {/* Metadata Card */}
              {metadata && (
                <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-lg">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-900">Generation Results</h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      metadata.avg_quality_score >= 85 
                        ? 'bg-green-100 text-green-700' 
                        : metadata.avg_quality_score >= 70
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      Quality: {metadata.avg_quality_score?.toFixed(1)}/100
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Slides Generated</p>
                      <p className="text-2xl font-bold text-gray-900">{metadata.slide_count}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Generation Method</p>
                      <p className="text-lg font-semibold text-purple-600 capitalize">
                        {metadata.generation_method || 'Agentic'}
                      </p>
                    </div>
                    {metadata.used_enhanced_context && (
                      <div className="col-span-2">
                        <div className="flex items-center space-x-2 text-sm text-green-700 bg-green-50 rounded-lg p-3">
                          <CheckCircle className="h-4 w-4" />
                          <span>Enhanced with RAG context</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Slide Preview */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-lg">
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Eye className="h-5 w-5 text-gray-600" />
                      <h3 className="text-lg font-bold text-gray-900">Slide Preview</h3>
                    </div>
                  </div>
                </div>
                <SlidePreview slides={slides} />
              </div>

              {/* Download Button */}
              <DownloadButton sessionId={sessionId} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default PPTDashboard;

