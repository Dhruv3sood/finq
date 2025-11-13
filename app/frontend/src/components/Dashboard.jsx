import React, { useState } from 'react';
import { 
  MessageCircle, 
  Presentation, 
  LayoutDashboard,
  FileText,
  Settings,
  TrendingUp,
  Menu,
  X
} from 'lucide-react';
import RAGDashboard from './rag/RAGDashboard';
import PPTDashboard from './ppt/PPTDashboard';
import Overview from './Overview';

function Dashboard() {
  const [activeView, setActiveView] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [stats, setStats] = useState({
    ragQueries: 0,
    pptsGenerated: 0,
    documentsProcessed: 0
  });

  const updateStats = (type) => {
    setStats(prev => ({
      ...prev,
      [type]: prev[type] + 1
    }));
  };

  const navigation = [
    { id: 'overview', name: 'Overview', icon: LayoutDashboard },
    { id: 'rag', name: 'RAG Chat', icon: MessageCircle },
    { id: 'ppt', name: 'PPT Generator', icon: Presentation },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside 
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gradient-to-b from-indigo-900 to-indigo-700 text-white transition-all duration-300 flex flex-col`}
      >
        {/* Logo & Toggle */}
        <div className="p-4 flex items-center justify-between border-b border-indigo-600">
          {sidebarOpen ? (
            <>
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-8 w-8 text-indigo-200" />
                <span className="text-xl font-bold">Q4++</span>
              </div>
              <button 
                onClick={() => setSidebarOpen(false)}
                className="p-1 hover:bg-indigo-600 rounded"
              >
                <X className="h-5 w-5" />
              </button>
            </>
          ) : (
            <button 
              onClick={() => setSidebarOpen(true)}
              className="p-1 hover:bg-indigo-600 rounded mx-auto"
            >
              <Menu className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`w-full flex items-center ${
                  sidebarOpen ? 'px-4' : 'justify-center'
                } py-3 rounded-lg transition-all ${
                  isActive 
                    ? 'bg-indigo-600 text-white shadow-lg' 
                    : 'text-indigo-100 hover:bg-indigo-600/50'
                }`}
              >
                <Icon className={`h-5 w-5 ${sidebarOpen ? 'mr-3' : ''}`} />
                {sidebarOpen && <span className="font-medium">{item.name}</span>}
              </button>
            );
          })}
        </nav>

        {/* Stats Footer */}
        {sidebarOpen && (
          <div className="p-4 border-t border-indigo-600 space-y-2">
            <div className="text-sm text-indigo-200">
              <div className="flex justify-between">
                <span>RAG Queries:</span>
                <span className="font-semibold">{stats.ragQueries}</span>
              </div>
              <div className="flex justify-between">
                <span>PPTs Created:</span>
                <span className="font-semibold">{stats.pptsGenerated}</span>
              </div>
              <div className="flex justify-between">
                <span>Documents:</span>
                <span className="font-semibold">{stats.documentsProcessed}</span>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                {navigation.find(n => n.id === activeView)?.name || 'Dashboard'}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {activeView === 'overview' && 'Welcome to your financial analysis dashboard'}
                {activeView === 'rag' && 'Ask questions about your financial documents'}
                {activeView === 'ppt' && 'Generate professional presentations from your data'}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                {new Date().toLocaleDateString('en-US', { 
                  weekday: 'short', 
                  year: 'numeric', 
                  month: 'short', 
                  day: 'numeric' 
                })}
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="p-8">
          {activeView === 'overview' && (
            <Overview 
              stats={stats}
              onNavigate={setActiveView}
            />
          )}
          {activeView === 'rag' && (
            <RAGDashboard 
              onQueryComplete={() => updateStats('ragQueries')}
              onDocumentProcessed={() => updateStats('documentsProcessed')}
            />
          )}
          {activeView === 'ppt' && (
            <PPTDashboard 
              onPPTGenerated={() => updateStats('pptsGenerated')}
              onDocumentProcessed={() => updateStats('documentsProcessed')}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;

