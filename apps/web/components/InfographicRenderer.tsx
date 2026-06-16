"use client";

import React from "react";

interface Annotation {
  label: string;
  x: number;
  y: number;
}

interface IconItem {
  type: string;
  label: string;
}

export interface InfographicData {
  title: string;
  subtitle?: string;
  main_subject?: {
    name: string;
    type: string; // e.g., 'building', 'map', 'concept'
    annotations: Annotation[];
  };
  icons: IconItem[];
  facts: string[];
  imageDataUrl?: string | null;
}

export const InfographicRenderer: React.FC<{ data: InfographicData }> = ({ data }) => {
  return (
    <div className="relative flex aspect-[16/9] w-full select-none flex-col overflow-hidden rounded-[34px] border border-black/10 bg-[#f7f8fa] font-sans">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(15,23,42,0.045)_1px,transparent_1px),linear-gradient(90deg,rgba(15,23,42,0.04)_1px,transparent_1px)] bg-[size:36px_36px] opacity-70" />

      {/* Main Content Area - Now 100% Width/Height */}
      <div className="relative flex-1 overflow-hidden group">
        {/* AI Generated Image as Background (Fills entire container) */}
        {data.imageDataUrl ? (
          <img
            src={data.imageDataUrl}
            alt={data.title}
            className="absolute inset-0 h-full w-full object-cover transition-transform duration-1000 group-hover:scale-[1.02]"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center animate-pulse">
            <p className="text-xs font-bold uppercase tracking-[0.5em] text-[#1d1d1f] opacity-15">Drafting visual page...</p>
          </div>
        )}

        {/* Floating Title (Minimalist Overlay) */}
        <div className="absolute top-8 left-8 z-20 pointer-events-none text-left">
          <h1 className="text-5xl font-semibold tracking-tight text-[#1d1d1f] drop-shadow-sm">{data.title}</h1>
          {data.subtitle && <p className="text-[10px] uppercase tracking-[0.4em] font-sans font-black opacity-40 mt-2 bg-white/40 backdrop-blur-sm px-2 py-1 inline-block rounded">{data.subtitle}</p>}
        </div>

        {/* SVG Overlay for Precise Annotations */}
        <svg className="absolute inset-0 w-full h-full z-10" viewBox="0 0 800 450">
          {/* Dynamic Annotations */}
          {data.main_subject?.annotations?.map((ann, i) => {
            const targetX = (ann.x / 100) * 800;
            const targetY = (ann.y / 100) * 450;
            const isRightSide = targetX > 400;
            const labelX = isRightSide ? targetX + 50 : targetX - 50;
            const labelY = targetY - 70;

            return (
              <g key={i} className="animate-in fade-in slide-in-from-bottom-2 duration-1000">
                <circle cx={targetX} cy={targetY} r="3" fill="#1d1d1f" />
                <circle cx={targetX} cy={targetY} r="8" fill="none" stroke="#1d1d1f" strokeWidth="0.5" opacity="0.4" />
                <path d={`M ${targetX} ${targetY} L ${labelX} ${labelY}`} fill="none" stroke="#1d1d1f" strokeWidth="1" />
                <foreignObject x={isRightSide ? labelX + 10 : labelX - 160} y={labelY - 15} width="150" height="60">
                  <div className={`text-[#1d1d1f] ${isRightSide ? 'text-left' : 'text-right'}`}>
                    <p className="text-[13px] font-bold leading-none border-b border-[#1d1d1f]/40 pb-1 mb-1 uppercase tracking-wider bg-white/30 backdrop-blur-[2px] inline-block">{ann.label}</p>
                    <p className="text-[8px] opacity-40 font-sans font-black leading-tight">DETAIL 0{i+1}</p>
                  </div>
                </foreignObject>
              </g>
            );
          })}
        </svg>

        {/* Floating Icons (Integrated into image area) */}
        <div className="absolute bottom-10 right-10 z-20 flex gap-4">
          {data.icons?.map((icon, i) => (
            <div key={i} className="group relative flex flex-col items-center">
              <div className="w-14 h-14 rounded-full bg-white/60 backdrop-blur-md border border-black/10 flex items-center justify-center text-3xl shadow-lg transition-all hover:scale-110 hover:bg-white/90">
                {icon.type === 'food' ? '🍲' : icon.type === 'landmark' ? '🏯' : icon.type === 'nature' ? '🌿' : '📍'}
              </div>
              <span className="absolute -bottom-6 text-[10px] font-bold tracking-widest uppercase opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 text-white px-2 py-0.5 rounded whitespace-nowrap">
                {icon.label}
              </span>
            </div>
          ))}
        </div>

        {/* Facts Overlay (Subtle Sidebar) */}
        <div className="absolute left-8 bottom-12 z-20 max-w-xs space-y-3 pointer-events-none text-left">
          {data.facts.slice(0, 3).map((fact, i) => (
            <div key={i} className="bg-white/40 backdrop-blur-sm border-l-2 border-black/20 p-2 rounded-r-md">
              <p className="text-[11px] leading-tight text-[#1d1d1f]/70 font-bold italic">{fact}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer (Simplified) */}
      <div className="px-8 py-4 bg-[#ece9de]/30 border-t border-[#1d1d1f]/10 flex items-center justify-between">
        <p className="text-[9px] text-[#1d1d1f]/30 font-black uppercase tracking-[0.3em]">Flipbook Procedural Engine // Reconstruction Alpha</p>
        <div className="flex gap-4 items-center">
           <div className="w-2 h-2 rounded-full bg-black/10 animate-pulse" />
           <span className="text-[9px] font-black tracking-[0.2em] uppercase opacity-20 italic">Verified Terminal Sync</span>
        </div>
      </div>
    </div>
  );
};
