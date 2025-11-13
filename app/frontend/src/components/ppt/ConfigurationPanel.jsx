import React, { useState, useEffect } from 'react';
import { Sparkles, Settings, Layers } from 'lucide-react';

const TEMPLATES = [
  { value: 'professional', label: 'Professional' },
  { value: 'modern', label: 'Modern' },
  { value: 'financial', label: 'Financial' },
  { value: 'executive', label: 'Executive' }
];

const THEMES = [
  { value: 'blue', label: 'Blue' },
  { value: 'green', label: 'Green' },
  { value: 'purple', label: 'Purple' },
  { value: 'orange', label: 'Orange' }
];

const AVAILABLE_SLIDES = [
  { value: 'title', label: 'Title Slide' },
  { value: 'executive', label: 'Executive Summary' },
  { value: 'vision_mission', label: 'Vision & Mission' },
  { value: 'financials', label: 'Financial Overview' },
  { value: 'assets', label: 'Assets Breakdown' },
  { value: 'liabilities', label: 'Liabilities Analysis' },
  { value: 'ratios', label: 'Financial Ratios' },
  { value: 'trends', label: 'Trends & Insights' },
  { value: 'company', label: 'Company Overview' },
  { value: 'products_services', label: 'Products & Services' },
  { value: 'markets_locations', label: 'Markets & Locations' },
  { value: 'leadership', label: 'Leadership Team' },
  { value: 'major_projects', label: 'Major Projects & Clients' },
  { value: 'conclusion', label: 'Conclusion' }
];

function ConfigurationPanel({ generating, onGenerate, recommendations }) {
  const [template, setTemplate] = useState('professional');
  const [theme, setTheme] = useState('blue');
  const [selectedSlides, setSelectedSlides] = useState([
    'title', 
    'executive', 
    'vision_mission',
    'financials', 
    'products_services',
    'markets_locations',
    'leadership',
    'major_projects',
    'conclusion'
  ]);

  useEffect(() => {
    if (recommendations && recommendations.length > 0) {
      setSelectedSlides(recommendations);
    }
  }, [recommendations]);

  const handleSlideToggle = (slideValue) => {
    setSelectedSlides(prev => 
      prev.includes(slideValue)
        ? prev.filter(s => s !== slideValue)
        : [...prev, slideValue]
    );
  };

  const handleGenerate = async () => {
    await onGenerate({
      template,
      theme,
      slides: selectedSlides
    });
  };

  return (
    <div className="space-y-6">
      {/* Settings Card */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center space-x-3 mb-6">
          <div className="bg-purple-100 p-2 rounded-lg">
            <Settings className="h-5 w-5 text-purple-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-900">Settings</h3>
        </div>
      
      <div className="space-y-4">
        <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Template Style</label>
          <select
            value={template}
              onChange={(e) => setTemplate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 transition"
          >
            {TEMPLATES.map(tpl => (
              <option key={tpl.value} value={tpl.value}>
                {tpl.label}
              </option>
            ))}
          </select>
        </div>

        <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Theme Color</label>
            <div className="grid grid-cols-2 gap-2">
              {THEMES.map(th => (
                <button
                  key={th.value}
                  onClick={() => setTheme(th.value)}
                  className={`px-4 py-2 rounded-lg border-2 transition ${
                    theme === th.value
                      ? 'border-purple-600 bg-purple-50 text-purple-900 font-semibold'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                  }`}
                >
                {th.label}
                </button>
            ))}
            </div>
          </div>
        </div>
      </div>

      {/* Slide Selection Card */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <Layers className="h-5 w-5 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900">Slides</h3>
          </div>
          <span className="text-sm font-semibold text-gray-600">
            {selectedSlides.length} selected
          </span>
        </div>

        {recommendations && (
          <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start space-x-2">
            <Sparkles className="h-4 w-4 text-blue-600 mt-0.5" />
            <p className="text-sm text-blue-800">
              <span className="font-semibold">AI Recommendations:</span> Based on your data, 
              {recommendations.length} slides are recommended
            </p>
          </div>
        )}
        
        <div className="border border-gray-200 rounded-lg p-3 max-h-64 overflow-y-auto">
          <div className="space-y-1">
              {AVAILABLE_SLIDES.map(slide => (
              <label 
                key={slide.value} 
                className={`flex items-center cursor-pointer p-3 rounded-lg transition ${
                  selectedSlides.includes(slide.value)
                    ? 'bg-purple-50 border-2 border-purple-200'
                    : 'hover:bg-gray-50 border-2 border-transparent'
                }`}
              >
                  <input
                    type="checkbox"
                    checked={selectedSlides.includes(slide.value)}
                    onChange={() => handleSlideToggle(slide.value)}
                  className="mr-3 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  />
                <span className="text-sm font-medium text-gray-800">{slide.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

      {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={generating || selectedSlides.length === 0}
        className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-xl font-bold text-lg hover:from-purple-700 hover:to-purple-600 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center justify-center space-x-2"
        >
        {generating ? (
          <>
            <Sparkles className="h-5 w-5 animate-pulse" />
            <span>Generating...</span>
          </>
        ) : (
          <>
            <Sparkles className="h-5 w-5" />
            <span>Generate Presentation</span>
          </>
        )}
        </button>
    </div>
  );
}

export default ConfigurationPanel;

