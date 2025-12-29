import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function SourceCard({ source, index }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const relevancePercentage = (source.relevance_score * 100).toFixed(1);
  
  const getRelevanceColor = (score) => {
    if (score > 0.8) return 'text-green-400';
    if (score > 0.6) return 'text-yellow-400';
    return 'text-orange-400';
  };

  return (
    <div className="bg-white/5 rounded-lg border border-white/10 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3 flex-1">
          <div className="flex-shrink-0 w-8 h-8 bg-financial-accent/20 rounded flex items-center justify-center">
            <FileText className="w-4 h-4 text-financial-accent" />
          </div>
          
          <div className="flex-1 text-left">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-white">
                {source.source}
              </span>
              {source.has_financial_keywords && (
                <span className="px-2 py-0.5 bg-financial-gold/20 text-financial-gold text-xs rounded-full flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  Financial
                </span>
              )}
            </div>
            <div className="text-xs text-gray-400">
              Chunk {source.chunk_index + 1}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className={`text-sm font-semibold ${getRelevanceColor(source.relevance_score)}`}>
              {relevancePercentage}%
            </div>
            <div className="text-xs text-gray-500">relevance</div>
          </div>
          
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 pt-2 border-t border-white/10">
              <p className="text-sm text-gray-300 leading-relaxed">
                {source.preview}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
