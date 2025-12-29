import React from 'react';
import { FileText, Trash2, Calendar, FileCheck } from 'lucide-react';
import { documentAPI } from '../services/api';

const DocumentList = ({ documents, onDocumentDeleted }) => {
  const handleDelete = async (documentId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await documentAPI.deleteDocument(documentId);
        if (onDocumentDeleted) {
          onDocumentDeleted(documentId);
        }
      } catch (error) {
        alert('Failed to delete document');
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4 text-gray-800">Your Documents</h2>
      
      {documents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
          <p>No documents uploaded yet</p>
          <p className="text-sm mt-2">Upload PDFs to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <div
              key={doc.document_id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <FileText className="h-6 w-6 text-primary-600 flex-shrink-0 mt-1" />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 truncate">
                      {doc.filename}
                    </h3>
                    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <FileCheck className="h-4 w-4" />
                        <span>{doc.pages} pages</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <FileCheck className="h-4 w-4" />
                        <span>{doc.chunks} chunks</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(doc.uploaded_at)}</span>
                      </div>
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                      {formatFileSize(doc.file_size)}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.document_id)}
                  className="text-red-500 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors duration-200"
                  title="Delete document"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentList;
