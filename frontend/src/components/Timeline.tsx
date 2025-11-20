import React from 'react';
import type { Span } from '../utils/transform';

interface TimelineProps {
    rootSpan: Span;
    onSelectSpan: (span: Span) => void;
    selectedSpanId: string | null;
}



export const Timeline: React.FC<TimelineProps> = ({ rootSpan, onSelectSpan, selectedSpanId }) => {
    // Calculate total duration from root span
    // Note: rootSpan.endTime might be undefined if still running, but for now assume completed traces
    const startTime = rootSpan.startTime;
    const endTime = rootSpan.children && rootSpan.children.length > 0
        ? Math.max(rootSpan.startTime + 1000, ...getAllEndTimes(rootSpan))
        : rootSpan.startTime + 1000; // Fallback

    const totalDuration = endTime - startTime;

    function getAllEndTimes(span: Span): number[] {
        let times = [span.end_time || span.startTime];
        if (span.children) {
            span.children.forEach(c => times.push(...getAllEndTimes(c)));
        }
        return times;
    }

    const renderSpan = (span: Span, depth: number) => {
        const spanStart = span.startTime;
        const spanEnd = span.end_time || span.startTime + 100; // Default width if missing
        const spanDuration = spanEnd - spanStart;

        const leftPercent = ((spanStart - startTime) / totalDuration) * 100;
        const widthPercent = Math.max(((spanDuration) / totalDuration) * 100, 0.5); // Min width

        // Color coding
        let barColor = 'bg-gray-400';
        if (span.attributes['gen_ai.system']) barColor = 'bg-green-500'; // LLM
        else if (span.attributes['db.system']) barColor = 'bg-blue-500'; // DB/Vector
        else if (span.status_code === 'ERROR') barColor = 'bg-red-500';

        return (
            <div key={span.spanId} className="mb-1 relative group">
                <div className="flex items-center h-8 hover:bg-gray-50 cursor-pointer" onClick={() => onSelectSpan(span)}>
                    <div className="w-48 flex-shrink-0 pl-2 text-sm truncate border-r border-gray-100 pr-2" style={{ paddingLeft: `${depth * 12 + 8}px` }}>
                        {span.name}
                    </div>
                    <div className="flex-grow relative h-full">
                        <div
                            className={`absolute top-2 h-4 rounded ${barColor} ${selectedSpanId === span.spanId ? 'ring-2 ring-blue-400' : ''}`}
                            style={{ left: `${leftPercent}%`, width: `${widthPercent}%` }}
                        ></div>
                    </div>
                </div>
                {span.children && span.children.map(child => renderSpan(child, depth + 1))}
            </div>
        );
    };

    return (
        <div className="flex-grow overflow-y-auto bg-white flex flex-col">
            <div className="h-10 border-b border-gray-200 flex items-center px-4 bg-gray-50 text-xs font-medium text-gray-500">
                <div className="w-48 flex-shrink-0">Span Name</div>
                <div className="flex-grow">Timeline ({totalDuration / 1000000}ms)</div>
            </div>
            <div className="p-2">
                {renderSpan(rootSpan, 0)}
            </div>
        </div>
    );
};
