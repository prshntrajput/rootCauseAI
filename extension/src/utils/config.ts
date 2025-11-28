/**
 * Configuration Manager
 * Handles VSCode settings for rootCauseAI
 */

import * as vscode from 'vscode';

export class Config {
    private config: vscode.WorkspaceConfiguration;

    constructor() {
        this.config = vscode.workspace.getConfiguration('rootcauseai');
    }

    public getBackendUrl(): string {
        return this.config.get<string>('backendUrl') || 'http://localhost:8000';
    }

    public getProvider(): string {
        return this.config.get<string>('provider') || 'gemini';
    }

    public getMaxRetries(): number {
        return this.config.get<number>('maxRetries') || 2;
    }

    public getAutoStartBackend(): boolean {
        return this.config.get<boolean>('autoStartBackend') || false;
    }

    public async setProvider(provider: string): Promise<void> {
        await this.config.update('provider', provider, vscode.ConfigurationTarget.Global);
    }

    public reload(): void {
        this.config = vscode.workspace.getConfiguration('rootcauseai');
    }
}
