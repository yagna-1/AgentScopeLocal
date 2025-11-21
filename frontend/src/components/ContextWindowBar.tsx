

interface ContextWindowBarProps {
    used: number;
    limit: number;
    warningThreshold?: number;
}

export function ContextWindowBar({ used, limit, warningThreshold = 0.8 }: ContextWindowBarProps) {
    const percentage = (used / limit) * 100;
    const isNearLimit = percentage >= warningThreshold * 100;

    // Determine color based on usage
    const getColor = () => {
        if (percentage >= 90) return '#ef4444'; // red
        if (percentage >= 80) return '#f59e0b'; // orange
        return '#10b981'; // green
    };

    return (
        <div className="context-window-container">
            <div className="context-header">
                <h4 className="context-title">
                    <span className="emoji">📊</span> Context Window Usage
                </h4>
                <div className="context-stats">
                    {used.toLocaleString()} / {limit.toLocaleString()} tokens
                    <span className="percentage">({percentage.toFixed(1)}%)</span>
                </div>
            </div>

            <div className="progress-bar-container">
                <div className="progress-track">
                    <div
                        className="progress-fill"
                        style={{
                            width: `${Math.min(percentage, 100)}%`,
                            backgroundColor: getColor()
                        }}
                    />
                </div>
            </div>

            {isNearLimit && (
                <div className="warning-message">
                    <span className="warning-icon">⚠️</span>
                    {percentage >= 90 ? 'Critical: Context window almost full' : 'Warning: Approaching context limit'}
                </div>
            )}

            <style>{`
        .context-window-container {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          background: #f9fafb;
          margin: 16px 0;
        }

        .context-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .context-title {
          margin: 0;
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

        .context-stats {
          font-size: 13px;
          color: #4b5563;
          font-weight: 500;
          font-family: 'Courier New', monospace;
        }

        .percentage {
          color: #6b7280;
          margin-left: 4px;
        }

        .progress-bar-container {
          margin: 8px 0;
        }

        .progress-track {
          height: 12px;
          background-color: #e5e7eb;
          border-radius: 6px;
          overflow: hidden;
          box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .progress-fill {
          height: 100%;
          transition: width 0.3s ease, background-color 0.3s ease;
          border-radius: 6px;
        }

        .warning-message {
          margin-top: 12px;
          padding: 8px 12px;
          background: #fef3c7;
          border: 1px solid #fbbf24;
          border-radius: 6px;
          color: #92400e;
          font-size: 13px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .warning-icon {
          font-size: 16px;
        }
      `}</style>
        </div>
    );
}
