import React, { useState } from 'react';
import { GitCompare, Loader2 } from 'lucide-react';
import { documentAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';

const ComparisonPanel = ({ documents }) => {
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [comparisonType, setComparisonType] = useState('general');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  const comparisonTypes = [
    { value: 'general', label: 'General Comparison' },
    { value: 'financial', label: 'Financial Performance' },
    { value: 'risks', label: 'Risk Analysis' },
    { value: 'opportunities', label: 'Opportunities' },
  ];

  const handleCompare = async () => {
    if (selectedDocs.length < 2) {
      alert('Please select at least 2 documents to compare');
      return;
    }

    if (selectedDocs.length > 5) {
      alert('Maximum 5 documents can be compared at once');
      return;
    }

    setLoading(true);
    try {
      const response = await documentAPI.compareDocuments({
        document_ids: selectedDocs,
        comparison_type: comparisonType,
      });
      setComparison(response);
    } catch (error) {
      alert('Failed to compare documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentToggle = (docId) => {
    setSelectedDocs(prev => 
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : prev.length < 5
        ? [...prev, docId]
        : prev
    );
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4 text-gray-800 flex items-center space-x-2">
        <GitCompare className="h-6 w-6 text-purple-500" />
        <span>Compare Documents</span>
      </h2>

      {documents.length < 2 ? (
        <div className="text-center py-8 text-gray-500">
          <p>Upload at least 2 documents to enable comparison</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Document Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Documents (2-5)
            </label>
            <div className="space-y-2 max-h-32 overflow-y-auto border border-gray-200 rounded-lg p-2">
              {documents.map(doc => (
                <label key={doc.document_id} className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                  <input
                    type="checkbox"
                    checked={selectedDocs.includes(doc.document_id)}
                    onChange={() => handleDocumentToggle(doc.document_id)}
                    disabled={!selectedDocs.includes(doc.document_id) && selectedDocs.length >= 5}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 disabled:opacity-50"
                  />
                  <span className="text-sm text-gray-700 truncate">{doc.filename}</span>
                </label>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {selectedDocs.length}/5 documents selected
            </p>
          </div>

          {/* Comparison Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Comparison Type
            </label>
            <select
              value={comparisonType}
              onChange={(e) => setComparisonType(e.target.value)}
              className="input-field"
            >
              {comparisonTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Compare Button */}
          <button
            onClick={handleCompare}
            disabled={loading || selectedDocs.length < 2}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Comparing...</span>
              </>
            ) : (
              <>
                <GitCompare className="h-5 w-5" />
                <span>Compare Documents</span>
              </>
            )}
          </button>

          {/* Results */}
          {comparison && (
            <div className="mt-4 space-y-4">
              {/* Main Comparison */}
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <h3 className="font-semibold text-purple-900 mb-2">Comparison Analysis</h3>
                <div className="prose prose-sm max-w-none text-gray-800">
                  <ReactMarkdown>{comparison.comparison}</ReactMarkdown>
                </div>
              </div>

              {/* Key Differences */}
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <h3 className="font-semibold text-orange-900 mb-2">Key Differences</h3>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                  {comparison.key_differences.map((diff, idx) => (
                    <li key={idx}>{diff}</li>
                  ))}
                </ul>
              </div>

              {/* Similarities */}
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2">Similarities</h3>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                  {comparison.similarities.map((sim, idx) => (
                    <li key={idx}>{sim}</li>
                  ))}
                </ul>
              </div>

              <div className="text-xs text-gray-500 text-center">
                Documents analyzed: {comparison.documents.join(', ')}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ComparisonPanel;
