import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface TraceSummary {
  trace_id: string;
  root_span_name: string;
  start_time: number;
  span_count: number;
}

export interface Span {
  span_id: string;
  trace_id: string;
  parent_span_id?: string;
  name: string;
  kind: string;
  start_time: number;
  end_time?: number;
  status_code: string;
  status_message?: string;
  attributes: Record<string, any>;
  events: any[];
  resource: Record<string, any>;
  children?: Span[];
}

export const fetchTraces = async (): Promise<TraceSummary[]> => {
  const response = await axios.get(`${API_BASE_URL}/traces`);
  return response.data;
};

export const fetchTrace = async (traceId: string): Promise<Span[]> => {
  const response = await axios.get(`${API_BASE_URL}/traces/${traceId}`);
  return response.data;
};

export const fetchVectors = async (spanId: string): Promise<any[]> => {
    const response = await axios.get(`${API_BASE_URL}/vectors/${spanId}`);
    return response.data;
};
