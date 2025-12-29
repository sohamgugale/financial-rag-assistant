import React, { useState } from 'react';
import { Lightbulb, TrendingUp, AlertTriangle, BarChart3, Loader2 } from 'lucide-react';
import { documentAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';

const InsightsPanel = ({ documents }) => {
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [insightType, setInsightType] = useState('summary');
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);

  const insightTypes = [
    { value: 'summary', label: 'Summary', icon: Lightbulb },
    { value: 'key_points', label: 'Key Points', icon: BarChart3 },
    { value: 'financial_metrics', label: 'Financial Metrics', icon: TrendingUp },
    { value: 'risks', label: 'Risks', icon: AlertTriangle },
  ];

  const handleExtractInsights = async () => {
    if (selectedDocs.length === 0) {
      alert('Please select at least one document');
      return;
    }

    setLoading(true);
    try {
      const response = await documentAPI.extractInsights({
        document_ids: selectedDocs,
        insight_type: insightType,
      });
      setInsights(response);
    } catch (error) {
      alert('Failed to extract insights');
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentToggle = (docId) => {
    setSelectedDocs(prev => 
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4 text-gray-800 flex items-center space-x-2">
        <Lightbulb className="h-6 w-6 text-yellow-500" />
        <span>Extract Insights</span>
      </h2>

      {documents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>Upload documents to extract insights</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Document Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Documents
            </label>
            <div className="space-y-2 max-h-32 overflow-y-auto border border-gray-200 rounded-lg p-2">
              {documents.map(doc => (
                <label key={doc.document_id} className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                  <input
                    type="checkbox"
                    checked={selectedDocs.includes(doc.document_id)}
                    onChange={() => handleDocumentToggle(doc.document_id)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700 truncate">{doc.filename}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Insight Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Insight Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              {insightTypes.map(type => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.value}
                    onClick={() => setInsightType(type.value)}
                    className={`flex items-center space-x-2 p-3 rounded-lg border-2 transition-all duration-200 ${
                      insightType === type.value
                        ? 'border-primary-600 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span className="text-sm font-medium">{type.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Extract Button */}
          <button
            onClick={handleExtractInsights}
            disabled={loading || selectedDocs.length === 0}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Lightbulb className="h-5 w-5" />
                <span>Extract Insights</span>
              </>
            )}
          </button>

          {/* Results */}
          {insights && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">
                {insightTypes.find(t => t.value === insights.insight_type)?.label}
              </h3>
              <div className="prose prose-sm max-w-none text-gray-800">
                <ReactMarkdown>{insights.content}</ReactMarkdown>
              </div>
              <div className="mt-3 pt-3 border-t border-blue-300">
                <p className="text-xs text-blue-700">
                  Analyzed: {insights.documents_analyzed.join(', ')}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InsightsPanel;
