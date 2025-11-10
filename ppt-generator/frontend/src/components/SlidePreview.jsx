import React from 'react';

function SlidePreview({ slides }) {
  if (!slides || slides.length === 0) {
    return (
      <div className="slide-preview">
        <p>No slides generated yet. Upload files and generate a presentation.</p>
      </div>
    );
  }

  const renderSlideContent = (slide) => {
    const content = slide.content || {};
    const title = content.title || slide.type || 'Slide';
    
    return (
      <div key={slide.type || slide.index} className="slide-item">
        <h3>{title}</h3>
        {content.highlights && (
          <ul>
            {content.highlights.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        )}
        {content.metrics && (
          <ul>
            {content.metrics.map((metric, i) => (
              <li key={i}>{metric.label}: {metric.value}</li>
            ))}
          </ul>
        )}
        {content.ratios && (
          <ul>
            {content.ratios.map((ratio, i) => (
              <li key={i}>{ratio.name}: {ratio.value} - {ratio.interpretation}</li>
            ))}
          </ul>
        )}
        {content.insights && (
          <ul>
            {content.insights.map((insight, i) => (
              <li key={i}>{insight}</li>
            ))}
          </ul>
        )}
        {content.key_takeaways && (
          <ul>
            {content.key_takeaways.map((takeaway, i) => (
              <li key={i}>{takeaway}</li>
            ))}
          </ul>
        )}
        {content.summary && (
          <div className="notes">
            <strong>Summary:</strong> {content.summary}
          </div>
        )}
        {content.insight && (
          <div className="notes">
            <strong>Insight:</strong> {content.insight}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="slide-preview">
      <h2>Slide Preview</h2>
      <div className="slides-container">
        {slides.map((slide, index) => renderSlideContent(slide))}
      </div>
    </div>
  );
}

export default SlidePreview;

