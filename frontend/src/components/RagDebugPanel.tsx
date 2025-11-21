/**
 * RAG Debug Panel Component
 * Shows similar vectors and helps debug retrieval quality
 */
import { useState, useEffect } from 'react';
import { Search, AlertCircle, Loader2, CheckCircle } from 'lucide-react';
import axios from 'axios';

interface SimilarVector {
    id: number;
    span_id: string;
    content: string;
    metadata: Record<string, any>;
    distance: number;
    similarity: number;
}

interface RAGDebugResult {
    query: {
        span_id: string;
        content: string;
    };
    similar_vectors: SimilarVector[];
}

interface RagDebugPanelProps {
    spanId: string;
    onClose: () => void;
}

export function RagDebugPanel({ spanId, onClose }: RagDebugPanelProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<RAGDebugResult | null>(null);
    const [limit, setLimit] = useState(10);

    const runDebug = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(`http://localhost:8000/api/debug-rag/${spanId}`, null, {
                params: { limit }
            });
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to debug RAG');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        runDebug();
    }, [spanId]);

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-blue-600 text-white">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Search className="w-6 h-6" />
                            <div>
                                <h2 className="text-xl font-bold">RAG Debugger</h2>
                                <p className="text-sm text-purple-100">Find what should have been retrieved</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-white hover:bg-white/20 rounded-lg px-3 py-1 transition"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading && (
                        <div className="flex items-center justify-center py-12">
                            <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                            <span className="ml-3 text-gray-600">Running similarity search...</span>
                        </div>
                    )}

                    {error && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                            <div>
                                <h3 className="font-semibold text-red-900">Error</h3>
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        </div>
                    )}

                    {result && (
                        <div className="space-y-6">
                            {/* Query */}
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                                    <Search className="w-4 h-4" />
                                    Query
                                </h3>
                                <p className="text-sm text-gray-700">{result.query.content}</p>
                            </div>

                            {/* Results */}
                            <div>
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="font-semibold text-gray-900">
                                        Top {result.similar_vectors.length} Similar Vectors
                                    </h3>
                                    <div className="flex items-center gap-2">
                                        <label className="text-sm text-gray-600">Limit:</label>
                                        <input
                                            type="number"
                                            min="1"
                                            max="50"
                                            value={limit}
                                            onChange={(e) => setLimit(parseInt(e.target.value))}
                                            className="w-16 px-2 py-1 border border-gray-300 rounded text-sm"
                                        />
                                        <button
                                            onClick={runDebug}
                                            className="px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
                                        >
                                            Refresh
                                        </button>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    {result.similar_vectors.map((vec, idx) => (
                                        <div
                                            key={vec.id}
                                            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
                                        >
                                            <div className="flex items-start justify-between mb-2">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-sm font-bold text-purple-600">#{idx + 1}</span>
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-24 bg-gray-200 rounded-full h-2">
                                                            <div
                                                                className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
                                                                style={{ width: `${vec.similarity * 100}%` }}
                                                            />
                                                        </div>
                                                        <span className="text-sm font-semibold text-gray-700">
                                                            {(vec.similarity * 100).toFixed(1)}%
                                                        </span>
                                                    </div>
                                                </div>
                                                {vec.similarity > 0.8 && (
                                                    <CheckCircle className="w-5 h-5 text-green-600" />
                                                )}
                                            </div>

                                            <p className="text-sm text-gray-800 mb-2">{vec.content}</p>

                                            <div className="flex items-center gap-4 text-xs text-gray-500">
                                                <span>Distance: {vec.distance.toFixed(4)}</span>
                                                <span>•</span>
                                                <span>Span: {vec.span_id.substring(0, 8)}...</span>
                                                {vec.metadata.model && (
                                                    <>
                                                        <span>•</span>
                                                        <span>Model: {vec.metadata.model}</span>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
