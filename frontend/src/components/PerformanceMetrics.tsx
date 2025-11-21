

interface PerformanceMetricsProps {
    ttft?: number;
    tps?: number;
    generationTime?: number;
    temperature?: number;
    topP?: number;
    maxTokens?: number;
    contextWindow?: number;
}

export function PerformanceMetrics({
    ttft,
    tps,
    generationTime,
    temperature,
    topP,
    maxTokens,
    contextWindow,
}: PerformanceMetricsProps) {
    const hasPerformanceMetrics = ttft !== undefined || tps !== undefined || generationTime !== undefined;
    const hasConfigMetrics = temperature !== undefined || topP !== undefined || maxTokens !== undefined;

    if (!hasPerformanceMetrics && !hasConfigMetrics) {
        return null;
    }

    return (
        <div className="performance-metrics-container">
            {hasPerformanceMetrics && (
                <div className="metric-card performance-card">
                    <h4 className="metric-title">
                        <span className="emoji">⚡</span> Performance Metrics
                    </h4>
                    <div className="metric-grid">
                        {ttft !== undefined && (
                            <div className="metric-item">
                                <div className="metric-label">Time to First Token</div>
                                <div className="metric-value ttft-value">{ttft.toFixed(0)}ms</div>
                            </div>
                        )}
                        {tps !== undefined && (
                            <div className="metric-item">
                                <div className="metric-label">Tokens per Second</div>
                                <div className="metric-value tps-value">{tps.toFixed(1)} tok/s</div>
                            </div>
                        )}
                        {generationTime !== undefined && (
                            <div className="metric-item">
                                <div className="metric-label">Total Generation Time</div>
                                <div className="metric-value time-value">{generationTime.toFixed(0)}ms</div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {hasConfigMetrics && (
                <div className="metric-card config-card">
                    <h4 className="metric-title">
                        <span className="emoji">⚙️</span> Model Configuration
                    </h4>
                    <div className="config-grid">
                        {temperature !== undefined && (
                            <div className="config-item">
                                <span className="config-label">Temperature:</span>
                                <span className="config-value">{temperature.toFixed(2)}</span>
                            </div>
                        )}
                        {topP !== undefined && (
                            <div className="config-item">
                                <span className="config-label">Top-p:</span>
                                <span className="config-value">{topP.toFixed(2)}</span>
                            </div>
                        )}
                        {maxTokens !== undefined && (
                            <div className="config-item">
                                <span className="config-label">Max Tokens:</span>
                                <span className="config-value">{maxTokens}</span>
                            </div>
                        )}
                        {contextWindow !== undefined && (
                            <div className="config-item">
                                <span className="config-label">Context Window:</span>
                                <span className="config-value">{contextWindow.toLocaleString()}</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            <style>{`
        .performance-metrics-container {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin: 16px 0;
        }

        .metric-card {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          background: #f9fafb;
        }

        .metric-title {
          margin: 0 0 12px 0;
          font-size: 14px;
          font-weight: 600;
          color: #374151;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .emoji {
          font-size: 16px;
        }

        .metric-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 12px;
        }

        .metric-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .metric-label {
          font-size: 12px;
          color: #6b7280;
          font-weight: 500;
        }

        .metric-value {
          font-size: 20px;
          font-weight: 700;
          font-family: 'Courier New', monospace;
        }

        .ttft-value {
          color: #3b82f6;
        }

        .tps-value {
          color: #10b981;
        }

        .time-value {
          color: #8b5cf6;
        }

        .config-grid {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .config-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 6px 0;
          border-bottom: 1px solid #e5e7eb;
        }

        .config-item:last-child {
          border-bottom: none;
        }

        .config-label {
          font-size: 13px;
          color: #6b7280;
          font-weight: 500;
        }

        .config-value {
          font-size: 13px;
          font-weight: 600;
          color: #111827;
          font-family: 'Courier New', monospace;
        }
      `}</style>
        </div>
    );
}
