export interface Span {
  spanId: string;
  parentSpanId?: string;
  name: string;
  startTime: number;
  end_time?: number;
  status_code?: string;
  attributes: Record<string, any>;
  children: Span[];
}

export function buildTraceTree(flatSpans: any[]): Span[] {
  const spanMap = new Map<string, Span>();
  const roots: Span[] = [];

  // 1. Initialize Spans
  flatSpans.forEach(s => {
    // Parse attributes if they are JSON strings
    let attributes = s.attributes;
    if (typeof attributes === 'string') {
        try {
            attributes = JSON.parse(attributes);
        } catch (e) {
            console.error("Failed to parse attributes", e);
            attributes = {};
        }
    }

    spanMap.set(s.span_id, { 
      spanId: s.span_id,
      parentSpanId: s.parent_span_id,
      name: s.name,
      startTime: s.start_time,
      end_time: s.end_time,
      status_code: s.status_code,
      attributes: attributes || {},
      children: [] 
    });
  });

  // 2. Build Hierarchy
  flatSpans.forEach(s => {
    const node = spanMap.get(s.span_id);
    if (node) {
        if (s.parent_span_id && spanMap.has(s.parent_span_id)) {
          const parent = spanMap.get(s.parent_span_id);
          parent?.children.push(node);
        } else {
          roots.push(node);
        }
    }
  });

  return roots;
}
