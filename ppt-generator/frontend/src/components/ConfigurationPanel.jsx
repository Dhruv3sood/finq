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
    <div className="configuration-panel">
      <h2>Configuration</h2>
      
      <div className="form-group">
        <label>Template Style:</label>
        <select value={template} onChange={(e) => onTemplateChange(e.target.value)}>
          {TEMPLATES.map(tpl => (
            <option key={tpl.value} value={tpl.value}>
              {tpl.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Theme Color:</label>
        <select value={theme} onChange={(e) => onThemeChange(e.target.value)}>
          {THEMES.map(th => (
            <option key={th.value} value={th.value}>
              {th.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Select Slides:</label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto', border: '1px solid #ccc', padding: '10px', borderRadius: '4px' }}>
          {AVAILABLE_SLIDES.map(slide => (
            <label key={slide.value} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
        <input 
                type="checkbox"
                checked={selectedSlides.includes(slide.value)}
                onChange={() => handleSlideToggle(slide.value)}
                style={{ marginRight: '8px' }}
        />
              {slide.label}
            </label>
          ))}
        </div>
      </div>

      <button onClick={handleGenerate} disabled={generating || selectedSlides.length === 0}>
        {generating ? 'Generating...' : 'Generate Presentation'}
      </button>
    </div>
  );
}

export default ConfigurationPanel;

