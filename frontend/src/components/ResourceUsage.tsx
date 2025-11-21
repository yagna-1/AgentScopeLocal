

interface ResourceUsageProps {
    cpuPercent?: number;
    memoryMb?: number;
    gpuUtilization?: number;
    gpuMemoryUsedMb?: number;
}

export function ResourceUsage({ cpuPercent, memoryMb, gpuUtilization, gpuMemoryUsedMb }: ResourceUsageProps) {
    const hasAnyMetric = cpuPercent !== undefined || memoryMb !== undefined ||
        gpuUtilization !== undefined || gpuMemoryUsedMb !== undefined;

    if (!hasAnyMetric) {
        return null;
    }

    return (
        <div className="resource-usage-container">
            <h4 className="resource-title">
                <span className="emoji">💻</span> Resource Usage
            </h4>

            <div className="resource-grid">
                {cpuPercent !== undefined && (
                    <div className="resource-item">
                        <div className="resource-icon">🔥</div>
                        <div className="resource-info">
                            <div className="resource-label">CPU</div>
                            <div className="resource-value cpu-value">{cpuPercent.toFixed(1)}%</div>
                        </div>
                    </div>
                )}

                {memoryMb !== undefined && (
                    <div className="resource-item">
                        <div className="resource-icon">🧠</div>
                        <div className="resource-info">
                            <div className="resource-label">Memory</div>
                            <div className="resource-value mem-value">{memoryMb.toFixed(0)} MB</div>
                        </div>
                    </div>
                )}

                {gpuUtilization !== undefined && (
                    <div className="resource-item">
                        <div className="resource-icon">🎮</div>
                        <div className="resource-info">
                            <div className="resource-label">GPU</div>
                            <div className="resource-value gpu-value">{gpuUtilization.toFixed(1)}%</div>
                        </div>
                    </div>
                )}

                {gpuMemoryUsedMb !== undefined && (
                    <div className="resource-item">
                        <div className="resource-icon">💾</div>
                        <div className="resource-info">
                            <div className="resource-label">GPU Memory</div>
                            <div className="resource-value gpu-mem-value">{gpuMemoryUsedMb.toFixed(0)} MB</div>
                        </div>
                    </div>
                )}
            </div>

            <style>{`
        .resource-usage-container {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          background: #f9fafb;
          margin: 16px 0;
        }

        .resource-title {
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

        .resource-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 12px;
        }

        .resource-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .resource-item:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .resource-icon {
          font-size: 24px;
          line-height: 1;
        }

        .resource-info {
          flex: 1;
          min-width: 0;
        }

        .resource-label {
          font-size: 11px;
          color: #9ca3af;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .resource-value {
          font-size: 16px;
          font-weight: 700;
          font-family: 'Courier New', monospace;
          margin-top: 2px;
        }

        .cpu-value {
          color: #ef4444;
        }

        .mem-value {
          color: #3b82f6;
        }

        .gpu-value {
          color: #8b5cf6;
        }

        .gpu-mem-value {
          color: #06b6d4;
        }
      `}</style>
        </div>
    );
}
