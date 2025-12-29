import React from 'react';
import { Database, Zap } from 'lucide-react';

export default function StatsPanel({ stats }) {
  return (
    <div className="flex items-center gap-4 px-4 py-2 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10">
      <div className="flex items-center gap-2">
        <Database className="w-4 h-4 text-financial-accent" />
        <div className="text-xs">
          <div className="text-gray-400">Documents</div>
          <div className="text-white font-semibold">{stats.documentCount}</div>
        </div>
      </div>
      
      <div className="w-px h-8 bg-white/10" />
      
      <div className="flex items-center gap-2">
        <Zap className="w-4 h-4 text-financial-gold" />
        <div className="text-xs">
          <div className="text-gray-400">Cache</div>
          <div className="text-white font-semibold">{stats.cacheSize}</div>
        </div>
      </div>
    </div>
  );
}
