import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, FileText } from 'lucide-react';

function SlidePreview({ slides }) {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  if (!slides || slides.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800">Slide Viewer</h2>
        <p className="text-gray-500">No slides generated yet. Upload files and generate a presentation.</p>
      </div>
    );
  }

  const currentSlide = slides[currentSlideIndex];
  const content = currentSlide.content || {};
  const title = content.title || currentSlide.type || 'Slide';

  const renderSlideContent = () => {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-white rounded-lg shadow-lg p-8 min-h-[500px] border-2 border-blue-100">
        <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-200">
          <FileText className="h-6 w-6 text-blue-600" />
          <h3 className="text-2xl font-bold text-gray-800">{title}</h3>
        </div>
        
        <div className="space-y-4">
          {/* Title Slide */}
          {currentSlide.type === 'title' && (
            <div className="text-center space-y-4">
              {content.subtitle && (
                <p className="text-lg text-gray-600">{content.subtitle}</p>
              )}
              {content.company_name && (
                <p className="text-xl font-semibold text-gray-800">{content.company_name}</p>
              )}
              {content.date && (
                <p className="text-sm text-gray-500">{content.date}</p>
              )}
            </div>
          )}

          {/* Executive Summary */}
          {content.highlights && (
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-3">Key Highlights</h4>
              <ul className="space-y-2">
                {content.highlights.map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Metrics */}
          {content.metrics && (
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-3">Financial Metrics</h4>
              <div className="grid grid-cols-2 gap-3">
                {content.metrics.map((metric, i) => (
                  <div key={i} className="bg-white p-3 rounded border border-gray-200">
                    <div className="text-sm text-gray-600">{metric.label}</div>
                    <div className="text-lg font-bold text-gray-800">{metric.value}</div>
                    {metric.trend && (
                      <div className={`text-xs mt-1 ${
                        metric.trend === 'up' ? 'text-green-600' : 
                        metric.trend === 'down' ? 'text-red-600' : 
                        'text-gray-600'
                      }`}>
                        {metric.trend}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ratios */}
          {content.ratios && (
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-3">Financial Ratios</h4>
              <div className="space-y-3">
                {content.ratios.map((ratio, i) => (
                  <div key={i} className="bg-white p-4 rounded border border-gray-200">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-semibold text-gray-800">{ratio.name}</span>
                      <span className="text-lg font-bold text-blue-600">{ratio.value}</span>
                    </div>
                    <p className="text-sm text-gray-600">{ratio.interpretation}</p>
                    {ratio.benchmark && (
                      <p className="text-xs text-gray-500 mt-1">Benchmark: {ratio.benchmark}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Assets/Liabilities Breakdown */}
          {(content.breakdown || content.total) && (
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-3">Breakdown</h4>
              {content.total && (
                <div className="mb-3 p-3 bg-blue-50 rounded">
                  <span className="text-sm text-gray-600">Total: </span>
                  <span className="text-lg font-bold text-gray-800">{content.total}</span>
                </div>
              )}
              {content.breakdown && (
                <div className="space-y-2">
                  {content.breakdown.map((item, i) => (
                    <div key={i} className="flex justify-between items-center p-2 bg-white rounded border border-gray-200">
                      <span className="text-gray-700">{item.category}</span>
                      <div className="flex items-center gap-3">
                        <span className="font-semibold text-gray-800">{item.amount}</span>
                        {item.percentage && (
                          <span className="text-sm text-gray-500">({item.percentage}%)</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Insights */}
          {content.insights && (
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-3">Insights</h4>
              <ul className="space-y-2">
                {content.insights.map((insight, i) => (
                  <li key={i} className="flex items-start gap-2 p-3 bg-yellow-50 rounded border-l-4 border-yellow-400">
                    <span className="text-yellow-600 mt-1">💡</span>
                    <span className="text-gray-700">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {content.recommendations && (
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-3">Recommendations</h4>
              <ul className="space-y-2">
                {content.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 p-3 bg-green-50 rounded border-l-4 border-green-400">
                    <span className="text-green-600 mt-1">✓</span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Key Takeaways */}
          {content.key_takeaways && (
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-3">Key Takeaways</h4>
              <ul className="space-y-2">
                {content.key_takeaways.map((takeaway, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">→</span>
                    <span className="text-gray-700">{takeaway}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Summary */}
          {content.summary && (
            <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
              <strong className="text-gray-800 block mb-2">Summary:</strong>
              <p className="text-gray-700">{content.summary}</p>
            </div>
          )}

          {/* Insight */}
          {content.insight && (
            <div className="mt-4 p-4 bg-green-50 border-l-4 border-green-500 rounded">
              <strong className="text-gray-800 block mb-2">Key Insight:</strong>
              <p className="text-gray-700">{content.insight}</p>
            </div>
          )}

          {/* Next Steps */}
          {content.next_steps && (
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-3">Next Steps</h4>
              <ul className="space-y-2">
                {content.next_steps.map((step, i) => (
                  <li key={i} className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                    <span className="text-gray-600 mt-1">{i + 1}.</span>
                    <span className="text-gray-700">{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">Slide Viewer</h2>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            Slide {currentSlideIndex + 1} of {slides.length}
          </span>
        </div>
      </div>

      {renderSlideContent()}

      {/* Navigation */}
      <div className="flex justify-between items-center mt-6 pt-4 border-t border-gray-200">
        <button
          onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
          disabled={currentSlideIndex === 0}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="h-5 w-5" />
          Previous
        </button>

        <div className="flex gap-2">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlideIndex(index)}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentSlideIndex ? 'bg-blue-600' : 'bg-gray-300'
              }`}
              aria-label={`Go to slide ${index + 1}`}
            />
          ))}
        </div>

        <button
          onClick={() => setCurrentSlideIndex(Math.min(slides.length - 1, currentSlideIndex + 1))}
          disabled={currentSlideIndex === slides.length - 1}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}

export default SlidePreview;
