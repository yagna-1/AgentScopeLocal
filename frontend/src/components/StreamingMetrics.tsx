
interface StreamingMetricsProps {
    streamingEnabled?: boolean;
    ttft?: number;
    chunkCount?: number;
    avgInterChunk?: number;
    perTokenLatency?: number;
    totalStreamTime?: number;
}

export function StreamingMetrics({
    streamingEnabled,
    ttft,
    chunkCount,
    avgInterChunk,
    perTokenLatency,
    totalStreamTime
}: StreamingMetricsProps) {
    // Only render if streaming was enabled
    if (!streamingEnabled) {
        return null;
    }

    return (
        <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200 shadow-sm">
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-lg">📡</span>
                Streaming Metrics
            </h4>

            <div className="grid grid-cols-2 gap-3">
                {/* TTFT (First Chunk) */}
                {ttft !== undefined && (
                    <div className="bg-white rounded-md p-3 shadow-sm border border-purple-100 hover:shadow-md transition-shadow">
                        <div className="text-xs text-gray-500 font-medium mb-1">First Chunk (TTFT)</div>
                        <div className="text-lg font-bold text-purple-600 font-mono">
                            {ttft.toFixed(0)}<span className="text-sm text-gray-500 font-normal ml-1">ms</span>
                        </div>
                    </div>
                )}

                {/* Chunk Count */}
                {chunkCount !== undefined && (
                    <div className="bg-white rounded-md p-3 shadow-sm border border-indigo-100 hover:shadow-md transition-shadow">
                        <div className="text-xs text-gray-500 font-medium mb-1">Chunks Received</div>
                        <div className="text-lg font-bold text-indigo-600 font-mono">
                            {chunkCount}<span className="text-sm text-gray-500 font-normal ml-1">chunks</span>
                        </div>
                    </div>
                )}

                {/* Average Inter-chunk */}
                {avgInterChunk !== undefined && (
                    <div className="bg-white rounded-md p-3 shadow-sm border border-purple-100 hover:shadow-md transition-shadow">
                        <div className="text-xs text-gray-500 font-medium mb-1">Avg Inter-chunk</div>
                        <div className="text-lg font-bold text-purple-600 font-mono">
                            {avgInterChunk.toFixed(1)}<span className="text-sm text-gray-500 font-normal ml-1">ms</span>
                        </div>
                    </div>
                )}

                {/* Per-token Latency */}
                {perTokenLatency !== undefined && (
                    <div className="bg-white rounded-md p-3 shadow-sm border border-indigo-100 hover:shadow-md transition-shadow">
                        <div className="text-xs text-gray-500 font-medium mb-1">Per-token Latency</div>
                        <div className="text-lg font-bold text-indigo-600 font-mono">
                            {perTokenLatency.toFixed(1)}<span className="text-sm text-gray-500 font-normal ml-1">ms/tok</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Total Streaming Time */}
            {totalStreamTime !== undefined && (
                <div className="mt-3 bg-gradient-to-r from-purple-100 to-indigo-100 rounded-md p-2 border border-purple-200">
                    <div className="text-xs text-purple-700 font-medium">
                        Total Streaming Time: <span className="font-bold font-mono">{totalStreamTime.toFixed(0)}ms</span>
                    </div>
                </div>
            )}

            {/* Streaming indicator */}
            <div className="mt-2 text-xs text-purple-600 flex items-center gap-1">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                Streaming response tracked
            </div>
        </div>
    );
}
