/**
 * Backend Client
 * Communicates with Python FastAPI backend
 */

import axios, { AxiosInstance } from 'axios';
import { Config } from './config';

export interface FixSuggestion {
    file_path: string;
    original_snippet: string;
    new_snippet: string;
    explanation: string;
    confidence: number;
    line_number?: number;
}

export interface AnalyzeResponse {
    status: string;
    parsed_error?: any;
    root_cause_analysis?: string;
    fixes: FixSuggestion[];
    execution_time: number;
    tokens_used: number;
    error_message?: string;
}

export interface ApplyFixResponse {
    success: boolean;
    message: string;
    fix_id?: string;
}

export interface HistoryItem {
    fix_id: string;
    file_path: string;
    timestamp: string;
    reverted: boolean;
}

export interface Stats {
    total_fixes: number;
    active_fixes: number;
    reverted_count: number;
    files_modified: number;
}

export class BackendClient {
    private client: AxiosInstance;
    private config: Config;

    constructor() {
        this.config = new Config();
        this.client = axios.create({
            baseURL: this.config.getBackendUrl(),
            timeout: 60000, // 60 seconds
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    public async checkHealth(): Promise<boolean> {
        try {
            const response = await this.client.get('/');
            return response.data.status === 'running';
        } catch (error) {
            return false;
        }
    }

    public async analyzeError(
        errorLog: string,
        projectRoot: string = '.'
    ): Promise<AnalyzeResponse> {
        const response = await this.client.post<AnalyzeResponse>('/analyze', {
            error_log: errorLog,
            project_root: projectRoot,
            provider: this.config.getProvider(),
            max_retries: this.config.getMaxRetries()
        });

        return response.data;
    }

    public async applyFix(
        fix: FixSuggestion,
        language: string,
        dryRun: boolean = false
    ): Promise<ApplyFixResponse> {
        const response = await this.client.post<ApplyFixResponse>('/apply-fix', {
            fix: fix,
            language: language,
            dry_run: dryRun
        });

        return response.data;
    }

    public async undoLastFix(): Promise<{ success: boolean; message: string }> {
        const response = await this.client.post('/undo');
        return response.data;
    }

    public async undoFix(fixId: string): Promise<{ success: boolean; message: string }> {
        const response = await this.client.post(`/undo/${fixId}`);
        return response.data;
    }

    public async getHistory(count: number = 10): Promise<HistoryItem[]> {
        const response = await this.client.get<{ fixes: HistoryItem[] }>('/history', {
            params: { count }
        });
        return response.data.fixes;
    }

    public async getStats(): Promise<Stats> {
        const response = await this.client.get<Stats>('/stats');
        return response.data;
    }
}
