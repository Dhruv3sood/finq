import React, { useState } from 'react';

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
  { value: 'financials', label: 'Financial Overview' },
  { value: 'assets', label: 'Assets Breakdown' },
  { value: 'liabilities', label: 'Liabilities Analysis' },
  { value: 'ratios', label: 'Financial Ratios' },
  { value: 'trends', label: 'Trends & Insights' },
  { value: 'company', label: 'Company Profile' },
  { value: 'conclusion', label: 'Conclusion' }
];

function ConfigurationPanel({ template, theme, onTemplateChange, onThemeChange, onGenerate, generating }) {
  const [selectedSlides, setSelectedSlides] = useState(['title', 'executive', 'financials', 'assets', 'liabilities', 'ratios', 'conclusion']);

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
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Configuration</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Template Style:</label>
          <select
            value={template}
            onChange={(e) => onTemplateChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {TEMPLATES.map(tpl => (
              <option key={tpl.value} value={tpl.value}>
                {tpl.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Theme Color:</label>
          <select
            value={theme}
            onChange={(e) => onThemeChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {THEMES.map(th => (
              <option key={th.value} value={th.value}>
                {th.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Slides:</label>
          <div className="border border-gray-300 rounded-lg p-4 max-h-48 overflow-y-auto">
            <div className="space-y-2">
              {AVAILABLE_SLIDES.map(slide => (
                <label key={slide.value} className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded">
                  <input
                    type="checkbox"
                    checked={selectedSlides.includes(slide.value)}
                    onChange={() => handleSlideToggle(slide.value)}
                    className="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="text-sm text-gray-700">{slide.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating || selectedSlides.length === 0}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {generating ? 'Generating...' : 'Generate Presentation'}
        </button>
      </div>
    </div>
  );
}

export default ConfigurationPanel;

