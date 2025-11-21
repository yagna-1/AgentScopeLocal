/**
 * Time Travel Fork Modal
 * Allows re-running LLM calls with modified prompts
 */
import React, { useState } from 'react';
import { GitBranch, Loader2, AlertCircle, Sparkles } from 'lucide-react';
import axios from 'axios';

interface ForkResult {
    original: {
        span_id: string;
        provider: string;
        model: string;
        prompt: string;
        completion: string;
        prompt_tokens?: number;
        completion_tokens?: number;
    };
    forked: {
        prompt: string;
        completion: string;
        model: string;
        usage: {
            prompt_tokens: number;
            completion_tokens: number;
            total_tokens: number;
        };
        finish_reason: string;
    };
}

interface ForkModalProps {
    spanId: string;
    originalPrompt: string;
    onClose: () => void;
}

export function ForkModal({ spanId, originalPrompt, onClose }: ForkModalProps) {
    const [modifiedPrompt, setModifiedPrompt] = useState(originalPrompt);
    const [temperature, setTemperature] = useState(0.7);
    const [maxTokens, setMaxTokens] = useState<number | undefined>(undefined);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<ForkResult | null>(null);

    const runFork = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(`http://localhost:8000/api/fork/${spanId}`, {
                modified_prompt: modifiedPrompt,
                temperature,
                max_tokens: maxTokens,
            });
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fork LLM call');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <GitBranch className="w-6 h-6" />
                            <div>
                                <h2 className="text-xl font-bold">Time Travel: Fork LLM Call</h2>
                                <p className="text-sm text-indigo-100">Replay with a modified prompt</p>
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
                    {!result ? (
                        <div className="space-y-6">
                            {/* Prompt Editor */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Modified Prompt
                                </label>
                                <textarea
                                    value={modifiedPrompt}
                                    onChange={(e) => setModifiedPrompt(e.target.value)}
                                    className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono text-sm"
                                    placeholder="Enter your modified prompt here..."
                                />
                            </div>

                            {/* Parameters */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                        Temperature
                                    </label>
                                    <input
                                        type="number"
                                        min="0"
                                        max="2"
                                        step="0.1"
                                        value={temperature}
                                        onChange={(e) => setTemperature(parseFloat(e.target.value))}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                        Max Tokens (Optional)
                                    </label>
                                    <input
                                        type="number"
                                        min="1"
                                        value={maxTokens || ''}
                                        onChange={(e) => setMaxTokens(e.target.value ? parseInt(e.target.value) : undefined)}
                                        placeholder="Auto"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                            </div>

                            {/* Error */}
                            {error && (
                                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                                    <div>
                                        <h3 className="font-semibold text-red-900">Error</h3>
                                        <p className="text-sm text-red-700">{error}</p>
                                    </div>
                                </div>
                            )}

                            {/* Action Button */}
                            <button
                                onClick={runFork}
                                disabled={loading || !modifiedPrompt.trim()}
                                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Running Fork...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-5 h-5" />
                                        Run Fork
                                    </>
                                )}
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Side-by-side comparison */}
                            <div className="grid grid-cols-2 gap-6">
                                {/* Original */}
                                <div className="border border-gray-300 rounded-lg overflow-hidden">
                                    <div className="bg-gray-100 px-4 py-2 border-b border-gray-300">
                                        <h3 className="font-semibold text-gray-900">Original</h3>
                                        <p className="text-xs text-gray-600">
                                            {result.original.provider} / {result.original.model}
                                        </p>
                                    </div>
                                    <div className="p-4 space-y-4">
                                        <div>
                                            <h4 className="text-xs font-semibold text-gray-600 mb-1">PROMPT</h4>
                                            <p className="text-sm text-gray-800 bg-gray-50 p-3 rounded border border-gray-200">
                                                {result.original.prompt}
                                            </p>
                                        </div>
                                        <div>
                                            <h4 className="text-xs font-semibold text-gray-600 mb-1">COMPLETION</h4>
                                            <p className="text-sm text-gray-800 bg-gray-50 p-3 rounded border border-gray-200">
                                                {result.original.completion}
                                            </p>
                                        </div>
                                        {result.original.prompt_tokens && (
                                            <div className="text-xs text-gray-600">
                                                Tokens: {result.original.prompt_tokens} + {result.original.completion_tokens}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Forked */}
                                <div className="border border-indigo-300 rounded-lg overflow-hidden">
                                    <div className="bg-indigo-100 px-4 py-2 border-b border-indigo-300">
                                        <h3 className="font-semibold text-indigo-900 flex items-center gap-2">
                                            <GitBranch className="w-4 h-4" />
                                            Forked
                                        </h3>
                                        <p className="text-xs text-indigo-600">{result.forked.model}</p>
                                    </div>
                                    <div className="p-4 space-y-4">
                                        <div>
                                            <h4 className="text-xs font-semibold text-gray-600 mb-1">PROMPT</h4>
                                            <p className="text-sm text-gray-800 bg-indigo-50 p-3 rounded border border-indigo-200">
                                                {result.forked.prompt}
                                            </p>
                                        </div>
                                        <div>
                                            <h4 className="text-xs font-semibold text-gray-600 mb-1">COMPLETION</h4>
                                            <p className="text-sm text-gray-800 bg-indigo-50 p-3 rounded border border-indigo-200">
                                                {result.forked.completion}
                                            </p>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            Tokens: {result.forked.usage.prompt_tokens} + {result.forked.usage.completion_tokens}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Try again button */}
                            <button
                                onClick={() => setResult(null)}
                                className="w-full bg-gray-200 text-gray-800 font-semibold py-2 px-6 rounded-lg hover:bg-gray-300"
                            >
                                Try Another Fork
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
