import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, X, FileText, CheckCircle2, AlertCircle } from 'lucide-react';

export default function DocumentUploader({ onUpload, onClose }) {
  const [uploadStatus, setUploadStatus] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploadStatus({ type: 'loading', message: `Uploading ${file.name}...` });

    try {
      await onUpload(file);
      setUploadStatus({ 
        type: 'success', 
        message: `Successfully uploaded ${file.name}` 
      });
      
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      setUploadStatus({ 
        type: 'error', 
        message: 'Upload failed. Please try again.' 
      });
    }
  }, [onUpload, onClose]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    multiple: false
  });

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-financial-navy rounded-2xl shadow-2xl border border-white/20 max-w-lg w-full overflow-hidden"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <h3 className="text-xl font-display font-bold text-white">
            Upload Document
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Upload Area */}
        <div className="p-6">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
              isDragActive
                ? 'border-financial-accent bg-financial-accent/10'
                : 'border-white/20 hover:border-financial-accent/50 hover:bg-white/5'
            }`}
          >
            <input {...getInputProps()} />
            
            {uploadStatus ? (
              <div>
                {uploadStatus.type === 'loading' && (
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-financial-accent border-t-transparent rounded-full animate-spin" />
                    <p className="text-white">{uploadStatus.message}</p>
                  </div>
                )}
                
                {uploadStatus.type === 'success' && (
                  <div className="flex flex-col items-center gap-4">
                    <CheckCircle2 className="w-12 h-12 text-green-500" />
                    <p className="text-green-500">{uploadStatus.message}</p>
                  </div>
                )}
                
                {uploadStatus.type === 'error' && (
                  <div className="flex flex-col items-center gap-4">
                    <AlertCircle className="w-12 h-12 text-red-500" />
                    <p className="text-red-500">{uploadStatus.message}</p>
                    <button
                      onClick={() => setUploadStatus(null)}
                      className="px-4 py-2 bg-financial-accent text-white rounded-lg"
                    >
                      Try Again
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <Upload className="w-16 h-16 text-financial-accent mx-auto mb-4" />
                
                {isDragActive ? (
                  <p className="text-lg text-white font-medium">
                    Drop your document here
                  </p>
                ) : (
                  <>
                    <p className="text-lg text-white font-medium mb-2">
                      Drag & drop or click to browse
                    </p>
                    <p className="text-sm text-gray-400 mb-4">
                      Supported formats: PDF, DOCX, TXT
                    </p>
                  </>
                )}

                <div className="flex items-center justify-center gap-4 mt-6">
                  {[
                    { ext: 'PDF', color: 'red' },
                    { ext: 'DOCX', color: 'blue' },
                    { ext: 'TXT', color: 'green' }
                  ].map((format) => (
                    <div key={format.ext} className="flex items-center gap-2 px-3 py-2 bg-white/5 rounded-lg">
                      <FileText className="w-4 h-4 text-gray-400" />
                      <span className="text-xs text-gray-400">{format.ext}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Tips */}
          {!uploadStatus && (
            <div className="mt-6 p-4 bg-financial-accent/10 border border-financial-accent/20 rounded-lg">
              <p className="text-sm text-gray-300">
                <span className="font-semibold text-financial-accent">Tip:</span> For best results,
                upload financial documents like earnings reports, 10-K filings, or research papers.
                The system will automatically extract and index the content.
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
