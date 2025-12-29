import React, { useState, useEffect } from 'react';
import { Brain, Github } from 'lucide-react';
import FileUpload from './components/FileUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import InsightsPanel from './components/InsightsPanel';
import ComparisonPanel from './components/ComparisonPanel';
import { documentAPI } from './services/api';
import './styles/index.css';

function App() {
  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await documentAPI.listDocuments();
      setDocuments(response.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    loadDocuments();
  };

  const handleDocumentDeleted = () => {
    loadDocuments();
  };

  const tabs = [
    { id: 'chat', label: 'Chat' },
    { id: 'insights', label: 'Insights' },
    { id: 'compare', label: 'Compare' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-primary-600 to-primary-700 p-3 rounded-lg shadow-lg">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Financial Research Assistant
                </h1>
                <p className="text-sm text-gray-600">
                  AI-powered document analysis with RAG
                </p>
              </div>
            </div>
            <a
              href="https://github.com/yourusername/financial-rag-assistant"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
            >
              <Github className="h-6 w-6" />
              <span className="hidden sm:inline">View on GitHub</span>
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Upload & Documents */}
          <div className="lg:col-span-1 space-y-6">
            <FileUpload onUploadSuccess={handleUploadSuccess} />
            <DocumentList
              documents={documents}
              onDocumentDeleted={handleDocumentDeleted}
            />
          </div>

          {/* Right Column - Main Interface */}
          <div className="lg:col-span-2">
            {/* Tabs */}
            <div className="bg-white rounded-t-lg shadow-md">
              <div className="flex border-b border-gray-200">
                {tabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 px-6 py-4 text-sm font-medium transition-colors duration-200 ${
                      activeTab === tab.id
                        ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Tab Content */}
            <div className="bg-white rounded-b-lg shadow-md">
              <div className="p-6">
                {activeTab === 'chat' && <ChatInterface documents={documents} />}
                {activeTab === 'insights' && <InsightsPanel documents={documents} />}
                {activeTab === 'compare' && <ComparisonPanel documents={documents} />}
              </div>
            </div>

            {/* Stats Card */}
            <div className="mt-6 bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">System Stats</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary-600">
                    {documents.length}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Documents</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary-600">
                    {documents.reduce((sum, doc) => sum + doc.pages, 0)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Total Pages</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary-600">
                    {documents.reduce((sum, doc) => sum + doc.chunks, 0)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Chunks</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-600">
          <p>Built with FastAPI, React, LangChain & OpenAI • RAG-powered Financial Analysis</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
