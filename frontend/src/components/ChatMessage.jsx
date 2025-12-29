import React from 'react';
import { motion } from 'framer-motion';
import { User, Bot, Clock, Zap } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import SourceCard from './SourceCard';

export default function ChatMessage({ message, isLatest }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-financial-accent to-financial-gold rounded-lg flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}

      <div className={`flex-1 max-w-3xl ${isUser ? 'flex justify-end' : ''}`}>
        <div className={`${
          isUser 
            ? 'bg-gradient-to-br from-financial-accent to-blue-600 text-white' 
            : 'bg-white/10 backdrop-blur-sm text-white border border-white/20'
        } rounded-2xl px-6 py-4 shadow-lg`}>
          
          {/* Message Content */}
          <div className="prose prose-invert max-w-none">
            {isUser ? (
              <p className="text-white">{message.content}</p>
            ) : (
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                  strong: ({ children }) => <strong className="text-financial-gold font-semibold">{children}</strong>,
                  ul: ({ children }) => <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>,
                  code: ({ inline, children }) => inline 
                    ? <code className="bg-white/10 px-2 py-1 rounded text-financial-gold font-mono text-sm">{children}</code>
                    : <code className="block bg-white/10 p-3 rounded-lg font-mono text-sm overflow-x-auto">{children}</code>
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>

          {/* Metadata (for assistant messages) */}
          {!isUser && message.processing_time && (
            <div className="mt-4 pt-4 border-t border-white/10 flex items-center gap-4 text-xs text-gray-400">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>{message.processing_time.toFixed(2)}s</span>
              </div>
              
              {message.tokens_used && (
                <div className="flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  <span>{message.tokens_used} tokens</span>
                </div>
              )}

              {message.search_strategy && (
                <div className="px-2 py-1 bg-white/10 rounded">
                  {message.search_strategy}
                </div>
              )}
            </div>
          )}

          {/* Sources */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <p className="text-xs font-semibold text-gray-400 mb-3">
                📚 Sources ({message.sources.length})
              </p>
              <div className="space-y-2">
                {message.sources.map((source, idx) => (
                  <SourceCard key={idx} source={source} index={idx + 1} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-gray-600 to-gray-700 rounded-lg flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </motion.div>
  );
}
