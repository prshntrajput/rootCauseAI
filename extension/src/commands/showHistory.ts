/**
 * Show History Command
 * Displays fix history
 */

import * as vscode from 'vscode';
import { BackendClient } from '../utils/backendClient';
import { Notifications } from '../utils/notifications';

export class ShowHistoryCommand {
    constructor(private client: BackendClient) {}

    public async execute(): Promise<void> {
        try {
            const history = await Notifications.showProgress('Loading history...', async () => {
                return await this.client.getHistory(20);
            });

            if (history.length === 0) {
                Notifications.showInfo('No fix history available');
                return;
            }

            // Create webview
            const panel = vscode.window.createWebviewPanel(
                'fixHistory',
                'Fix History',
                vscode.ViewColumn.Two,
                { enableScripts: true }
            );

            panel.webview.html = this.getHistoryHtml(history);

        } catch (error: any) {
            Notifications.showError(`Error: ${error.message}`);
        }
    }

    private getHistoryHtml(history: any[]): string {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-foreground);
                        padding: 20px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    th, td {
                        padding: 10px;
                        text-align: left;
                        border-bottom: 1px solid var(--vscode-panel-border);
                    }
                    th {
                        background: var(--vscode-editor-background);
                        font-weight: bold;
                    }
                    .active { color: #4ec9b0; }
                    .reverted { color: #f14c4c; }
                </style>
            </head>
            <body>
                <h1>📜 Fix History</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Fix ID</th>
                            <th>File</th>
                            <th>Timestamp</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${history.map(fix => `
                            <tr>
                                <td>de>${fix.fix_id}</code></td>
                                <td>${fix.file_path}</td>
                                <td>${new Date(fix.timestamp).toLocaleString()}</td>
                                <td class="${fix.reverted ? 'reverted' : 'active'}">
                                    ${fix.reverted ? '🔴 Reverted' : '✅ Active'}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </body>
            </html>
        `;
    }
}
