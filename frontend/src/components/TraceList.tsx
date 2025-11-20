import React from 'react';
import type { TraceSummary } from '../api';
import { format } from 'date-fns';
import { Activity } from 'lucide-react';

interface TraceListProps {
    traces: TraceSummary[];
    selectedTraceId: string | null;
    onSelectTrace: (traceId: string) => void;
}

export const TraceList: React.FC<TraceListProps> = ({ traces, selectedTraceId, onSelectTrace }) => {
    return (
        <div className="w-80 border-r border-gray-200 h-full overflow-y-auto bg-gray-50">
            <div className="p-4 border-b border-gray-200 bg-white">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-600" />
                    Traces
                </h2>
            </div>
            <ul>
                {traces.map((trace) => (
                    <li
                        key={trace.trace_id}
                        className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors ${selectedTraceId === trace.trace_id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                            }`}
                        onClick={() => onSelectTrace(trace.trace_id)}
                    >
                        <div className="font-medium text-gray-900 truncate">{trace.root_span_name}</div>
                        <div className="text-xs text-gray-500 mt-1 flex justify-between">
                            <span>{format(new Date(trace.start_time / 1000000), 'HH:mm:ss')}</span>
                            <span>{trace.span_count} spans</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1 font-mono truncate">
                            {trace.trace_id.substring(0, 8)}...
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
};
