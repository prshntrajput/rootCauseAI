/**
 * Explain Error Command
 * Shows detailed error analysis without fixing
 */

import * as vscode from 'vscode';
import { BackendClient } from '../utils/backendClient';
import { Notifications } from '../utils/notifications';

export class ExplainErrorCommand {
    constructor(private client: BackendClient) {}

    public async execute(): Promise<void> {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                Notifications.showWarning('No active editor');
                return;
            }

            // Get selected text (error log)
            const selection = editor.selection;
            const errorLog = editor.document.getText(selection);

            if (!errorLog) {
                Notifications.showWarning('Please select an error message');
                return;
            }

            // Analyze error
            const result = await Notifications.showProgress('Analyzing error...', async () => {
                return await this.client.analyzeError(
                    errorLog,
                    vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.'
                );
            });

            // Show explanation
            this.showExplanation(result);

        } catch (error: any) {
            Notifications.showError(`Error: ${error.message}`);
        }
    }

    private showExplanation(result: any): void {
        const panel = vscode.window.createWebviewPanel(
            'errorExplanation',
            'Error Explanation',
            vscode.ViewColumn.Two,
            {}
        );

        const parsedError = result.parsed_error;
        const rootCause = result.root_cause_analysis || 'Analysis not available';
        const fixes = result.fixes || [];

        panel.webview.html = `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-foreground);
                        padding: 20px;
                        line-height: 1.6;
                    }
                    h1, h2 {
                        color: var(--vscode-textLink-foreground);
                    }
                    .section {
                        background: var(--vscode-editor-background);
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                    }
                    .badge {
                        display: inline-block;
                        padding: 3px 8px;
                        border-radius: 3px;
                        font-size: 12px;
                        margin: 5px 5px 5px 0;
                    }
                    .error { background: #f14c4c; color: white; }
                    .warning { background: #cca700; color: white; }
                    .info { background: #007acc; color: white; }
                </style>
            </head>
            <body>
                <h1>🔍 Error Explanation</h1>
                
                ${parsedError ? `
                    <div class="section">
                        <h2>Error Details</h2>
                        <span class="badge ${parsedError.severity}">${parsedError.severity}</span>
                        <span class="badge info">${parsedError.language}</span>
                        <span class="badge info">${parsedError.category}</span>
                        <p><strong>Type:</strong> ${parsedError.error_type}</p>
                        <p><strong>Message:</strong> ${parsedError.message}</p>
                        ${parsedError.framework ? `<p><strong>Framework:</strong> ${parsedError.framework}</p>` : ''}
                    </div>
                ` : ''}
                
                <div class="section">
                    <h2>Root Cause Analysis</h2>
                    <p style="white-space: pre-wrap;">${rootCause}</p>
                </div>
                
                ${fixes.length > 0 ? `
                    <div class="section">
                        <h2>Suggested Fixes (${fixes.length})</h2>
                        ${fixes.map((fix: any, i: number) => `
                            <p><strong>Fix ${i + 1}:</strong> ${fix.explanation}</p>
                            <p><em>Confidence: ${(fix.confidence * 100).toFixed(0)}%</em></p>
                        `).join('')}
                    </div>
                ` : '<p><em>No fixes available</em></p>'}
                
                <div class="section">
                    <h2>Execution Stats</h2>
                    <p>⏱️ Time: ${result.execution_time?.toFixed(2)}s</p>
                    <p>🪙 Tokens: ${result.tokens_used}</p>
                </div>
            </body>
            </html>
        `;
    }
}
