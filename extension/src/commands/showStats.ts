/**
 * Show Stats Command
 * Displays usage statistics
 */

import * as vscode from 'vscode';
import { BackendClient } from '../utils/backendClient';
import { Notifications } from '../utils/notifications';

export class ShowStatsCommand {
    constructor(private client: BackendClient) {}

    public async execute(): Promise<void> {
        try {
            const stats = await Notifications.showProgress('Loading stats...', async () => {
                return await this.client.getStats();
            });

            const panel = vscode.window.createWebviewPanel(
                'fixStats',
                'Statistics',
                vscode.ViewColumn.Two,
                {}
            );

            panel.webview.html = `
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {
                            font-family: var(--vscode-font-family);
                            color: var(--vscode-foreground);
                            padding: 20px;
                        }
                        .stats-grid {
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            gap: 20px;
                            margin-top: 20px;
                        }
                        .stat-card {
                            background: var(--vscode-editor-background);
                            padding: 20px;
                            border-radius: 5px;
                            text-align: center;
                        }
                        .stat-number {
                            font-size: 48px;
                            font-weight: bold;
                            color: var(--vscode-textLink-foreground);
                        }
                        .stat-label {
                            font-size: 14px;
                            margin-top: 10px;
                            opacity: 0.8;
                        }
                    </style>
                </head>
                <body>
                    <h1>📊 rootCauseAI Statistics</h1>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${stats.total_fixes}</div>
                            <div class="stat-label">Total Fixes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.active_fixes}</div>
                            <div class="stat-label">Active Fixes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.reverted_count}</div>
                            <div class="stat-label">Reverted</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.files_modified}</div>
                            <div class="stat-label">Files Modified</div>
                        </div>
                    </div>
                </body>
                </html>
            `;
        } catch (error: any) {
            Notifications.showError(`Error: ${error.message}`);
        }
    }
}
