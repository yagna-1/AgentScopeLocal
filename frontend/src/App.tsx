import { useEffect, useState } from 'react';
import { TraceList } from './components/TraceList';
import { Timeline } from './components/Timeline';
import { SpanDetails } from './components/SpanDetails';
import { fetchTraces, fetchTrace } from './api';
import type { TraceSummary } from './api';
import { buildTraceTree } from './utils/transform';
import type { Span } from './utils/transform';
import { Layout } from 'lucide-react';

function App() {
  const [traces, setTraces] = useState<TraceSummary[]>([]);
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [rootSpan, setRootSpan] = useState<Span | null>(null);
  const [selectedSpan, setSelectedSpan] = useState<Span | null>(null);

  useEffect(() => {
    loadTraces();
  }, []);

  const loadTraces = async () => {
    try {
      const data = await fetchTraces();
      setTraces(data);
      if (data.length > 0 && !selectedTraceId) {
        // Select first trace by default
        handleSelectTrace(data[0].trace_id);
      }
    } catch (e) {
      console.error("Failed to load traces", e);
    }
  };

  const handleSelectTrace = async (traceId: string) => {
    setSelectedTraceId(traceId);
    setSelectedSpan(null);
    try {
      const flatSpans = await fetchTrace(traceId);
      const roots = buildTraceTree(flatSpans);
      if (roots.length > 0) {
        setRootSpan(roots[0]);
      }
    } catch (e) {
      console.error("Failed to load trace details", e);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-white text-gray-900 font-sans overflow-hidden">
      <TraceList
        traces={traces}
        selectedTraceId={selectedTraceId}
        onSelectTrace={handleSelectTrace}
      />

      <div className="flex-grow flex flex-col h-full overflow-hidden">
        <header className="h-14 border-b border-gray-200 flex items-center px-6 bg-white shadow-sm z-10">
          <Layout className="w-5 h-5 text-gray-500 mr-2" />
          <h1 className="font-bold text-gray-800">AgentScope Local</h1>
          <div className="ml-auto">
            <button onClick={loadTraces} className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded text-gray-600 transition-colors">
              Refresh
            </button>
          </div>
        </header>

        <div className="flex-grow flex overflow-hidden">
          {rootSpan ? (
            <Timeline
              rootSpan={rootSpan}
              onSelectSpan={setSelectedSpan}
              selectedSpanId={selectedSpan?.spanId || null}
            />
          ) : (
            <div className="flex-grow flex items-center justify-center text-gray-400">
              Select a trace to view timeline
            </div>
          )}

          <SpanDetails span={selectedSpan} />
        </div>
      </div>
    </div>
  );
}

export default App;
