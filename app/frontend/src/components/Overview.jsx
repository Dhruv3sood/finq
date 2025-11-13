import React from 'react';
import { 
  MessageCircle, 
  Presentation, 
  FileText,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Sparkles
} from 'lucide-react';

function Overview({ stats, onNavigate }) {
  const features = [
    {
      id: 'rag',
      icon: MessageCircle,
      title: 'RAG Chat',
      description: 'Chat with your financial documents using advanced AI. Ask questions and get instant, accurate answers with citations.',
      color: 'blue',
      features: [
        'Intelligent query routing',
        'Context-aware responses',
        'Source citations',
        'Grounding validation'
      ]
    },
    {
      id: 'ppt',
      icon: Presentation,
      title: 'PPT Generator',
      description: 'Generate professional presentations automatically. AI-powered slide creation with financial analysis and insights.',
      color: 'purple',
      features: [
        'Automated slide generation',
        'Financial analysis',
        'Quality scoring',
        'Multiple templates'
      ]
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: {
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        text: 'text-blue-900',
        icon: 'text-blue-600',
        button: 'bg-blue-600 hover:bg-blue-700',
        badge: 'bg-blue-100 text-blue-700'
      },
      purple: {
        bg: 'bg-purple-50',
        border: 'border-purple-200',
        text: 'text-purple-900',
        icon: 'text-purple-600',
        button: 'bg-purple-600 hover:bg-purple-700',
        badge: 'bg-purple-100 text-purple-700'
      }
    };
    return colors[color];
  };

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-start justify-between">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6" />
              <h2 className="text-3xl font-bold">Welcome to Q4++</h2>
            </div>
            <p className="text-indigo-100 text-lg max-w-2xl">
              Your AI-powered financial analysis platform. Process documents, get instant answers, 
              and create professional presentations with advanced agentic architecture.
            </p>
            <div className="flex items-center space-x-2 text-sm text-indigo-200">
              <CheckCircle className="h-4 w-4" />
              <span>Powered by GPT-4o & Advanced RAG</span>
            </div>
          </div>
          <TrendingUp className="h-16 w-16 text-indigo-200" />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">RAG Queries</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.ragQueries}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <MessageCircle className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">PPTs Generated</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.pptsGenerated}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <Presentation className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Documents Processed</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.documentsProcessed}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <FileText className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {features.map((feature) => {
          const Icon = feature.icon;
          const colors = getColorClasses(feature.color);
          
          return (
            <div 
              key={feature.id}
              className={`${colors.bg} ${colors.border} border-2 rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all`}
            >
              <div className="flex items-start space-x-4">
                <div className={`${colors.icon} bg-white p-3 rounded-xl shadow-md`}>
                  <Icon className="h-8 w-8" />
                </div>
                <div className="flex-1">
                  <h3 className={`text-2xl font-bold ${colors.text} mb-2`}>
                    {feature.title}
                  </h3>
                  <p className="text-gray-700 mb-4">
                    {feature.description}
                  </p>
                  
                  <div className="space-y-2 mb-6">
                    {feature.features.map((item, idx) => (
                      <div key={idx} className="flex items-center space-x-2">
                        <CheckCircle className={`h-4 w-4 ${colors.icon}`} />
                        <span className="text-sm text-gray-700">{item}</span>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => onNavigate(feature.id)}
                    className={`${colors.button} text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 transition-all shadow-md hover:shadow-lg`}
                  >
                    <span>Get Started</span>
                    <ArrowRight className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Tips */}
      <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Tips</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="bg-blue-100 p-2 rounded">
                <FileText className="h-4 w-4 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900">Upload Documents</h4>
            </div>
            <p className="text-sm text-gray-600">
              Upload balance sheets and company profiles in PDF or text format
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="bg-purple-100 p-2 rounded">
                <MessageCircle className="h-4 w-4 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900">Ask Questions</h4>
            </div>
            <p className="text-sm text-gray-600">
              Use RAG Chat to ask questions about your financial data with AI assistance
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="bg-green-100 p-2 rounded">
                <Presentation className="h-4 w-4 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900">Generate PPTs</h4>
            </div>
            <p className="text-sm text-gray-600">
              Create professional presentations automatically with AI-powered insights
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Overview;

