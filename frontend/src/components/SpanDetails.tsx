import React, { useEffect, useState } from 'react';
import type { Span } from '../utils/transform';
import { fetchVectors } from '../api';
import { Database, MessageSquare, Code, Search, GitBranch } from 'lucide-react';

interface SpanDetailsProps {
    span: Span | null;
    onOpenRagDebug?: (spanId: string) => void;
    onOpenFork?: (spanId: string, prompt: string) => void;
}

export const SpanDetails: React.FC<SpanDetailsProps> = ({ span, onOpenRagDebug, onOpenFork }) => {
    const [vectors, setVectors] = useState<any[]>([]);

    useEffect(() => {
        if (span) {
            fetchVectors(span.spanId).then(setVectors).catch(console.error);
        } else {
            setVectors([]);
        }
    }, [span]);

    if (!span) {
        return (
            <div className="w-96 border-l border-gray-200 bg-gray-50 p-8 text-center text-gray-500">
                Select a span to view details
            </div>
        );
    }

    const isLLM = !!span.attributes['gen_ai.system'];
    const isDB = !!span.attributes['db.system'];
    const hasVectors = vectors.length > 0;
    const prompt = span.attributes['gen_ai.prompt'] as string || '';

    return (
        <div className="w-96 border-l border-gray-200 bg-white h-full overflow-y-auto flex flex-col shadow-xl z-10">
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <h3 className="font-semibold text-lg truncate" title={span.name}>{span.name}</h3>
                <div className="text-xs text-gray-500 font-mono mt-1">{span.spanId}</div>
                <div className="mt-2 flex gap-2">
                    {isLLM && <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1"><MessageSquare className="w-3 h-3" /> LLM</span>}
                    {isDB && <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full flex items-center gap-1"><Database className="w-3 h-3" /> Vector DB</span>}
                </div>

                {/* Action Buttons */}
                <div className="mt-3 flex flex-col gap-2">
                    {hasVectors && onOpenRagDebug && (
                        <button
                            onClick={() => onOpenRagDebug(span.spanId)}
                            className="w-full flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-all shadow-md hover:shadow-lg"
                        >
                            <Search className="w-4 h-4" />
                            Debug RAG
                        </button>
                    )}
                    {isLLM && prompt && onOpenFork && (
                        <button
                            onClick={() => onOpenFork(span.spanId, prompt)}
                            className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-all shadow-md hover:shadow-lg"
                        >
                            <GitBranch className="w-4 h-4" />
                            Time Travel Fork
                        </button>
                    )}
                </div>
            </div>

            <div className="p-4 space-y-6">
                {/* Attributes */}
                <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-2">
                        <Code className="w-4 h-4" /> Attributes
                    </h4>
                    <div className="bg-gray-50 rounded p-2 text-xs font-mono overflow-x-auto border border-gray-100">
                        <pre>{JSON.stringify(span.attributes, null, 2)}</pre>
                    </div>
                </div>

                {/* LLM Specifics */}
                {isLLM && (
                    <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Prompt</h4>
                        <div className="bg-gray-50 rounded p-2 text-xs whitespace-pre-wrap border border-gray-100">
                            {prompt || 'N/A'}
                        </div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2 mt-4">Completion</h4>
                        <div className="bg-green-50 rounded p-2 text-xs whitespace-pre-wrap border border-green-100">
                            {span.attributes['gen_ai.completion'] || 'N/A'}
                        </div>
                    </div>
                )}

                {/* Vector Data */}
                {hasVectors && (
                    <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-2">
                            <Database className="w-4 h-4" /> Vector Operations
                        </h4>
                        {vectors.map((v, i) => (
                            <div key={i} className="mb-2 p-2 bg-blue-50 rounded border border-blue-100 text-xs">
                                <div className="font-semibold text-blue-800 mb-1">{v.metadata?.type || 'Vector Log'}</div>
                                <div className="italic text-gray-600 mb-1">"{v.content || v.text_content}"</div>
                                <pre className="text-gray-500 text-[10px]">{JSON.stringify(v.metadata, null, 2)}</pre>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
