import React, { useEffect, useState } from 'react';
import type { Span } from '../utils/transform';
import { fetchVectors } from '../api';
import { Database, MessageSquare, Code } from 'lucide-react';

interface SpanDetailsProps {
    span: Span | null;
}

export const SpanDetails: React.FC<SpanDetailsProps> = ({ span }) => {
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

    return (
        <div className="w-96 border-l border-gray-200 bg-white h-full overflow-y-auto flex flex-col shadow-xl z-10">
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <h3 className="font-semibold text-lg truncate" title={span.name}>{span.name}</h3>
                <div className="text-xs text-gray-500 font-mono mt-1">{span.spanId}</div>
                <div className="mt-2 flex gap-2">
                    {isLLM && <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1"><MessageSquare className="w-3 h-3" /> LLM</span>}
                    {isDB && <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full flex items-center gap-1"><Database className="w-3 h-3" /> Vector DB</span>}
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
                            {span.attributes['gen_ai.prompt'] || 'N/A'}
                        </div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2 mt-4">Completion</h4>
                        <div className="bg-green-50 rounded p-2 text-xs whitespace-pre-wrap border border-green-100">
                            {span.attributes['gen_ai.completion'] || 'N/A'}
                        </div>
                    </div>
                )}

                {/* Vector Data */}
                {vectors.length > 0 && (
                    <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-2">
                            <Database className="w-4 h-4" /> Vector Operations
                        </h4>
                        {vectors.map((v, i) => (
                            <div key={i} className="mb-2 p-2 bg-blue-50 rounded border border-blue-100 text-xs">
                                <div className="font-semibold text-blue-800 mb-1">{v.vector_type || 'Vector Log'}</div>
                                <div className="italic text-gray-600 mb-1">"{v.text_content}"</div>
                                <pre className="text-gray-500 text-[10px]">{JSON.stringify(v.metadata, null, 2)}</pre>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
