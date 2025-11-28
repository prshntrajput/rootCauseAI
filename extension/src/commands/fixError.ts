/**
 * Fix Error Command
 * Main command to analyze and fix errors
 */

import * as vscode from 'vscode';
import { BackendClient, FixSuggestion } from '../utils/backendClient';
import { Notifications } from '../utils/notifications';

export class FixErrorCommand {
    constructor(private client: BackendClient) {}

    public async execute(): Promise<void> {
        try {
            // Check backend health
            const isHealthy = await this.client.checkHealth();
            if (!isHealthy) {
                Notifications.showError(
                    'Backend server is not running. Please start it with: python backend/server.py'
                );
                return;
            }

            // Get error log
            const errorLog = await this.getErrorLog();
            if (!errorLog) {
                Notifications.showWarning('No error log provided');
                return;
            }

            // Analyze error
            const result = await Notifications.showProgress('Analyzing error...', async (progress) => {
                progress.report({ message: 'Parsing error...' });
                const result = await this.client.analyzeError(
                    errorLog,
                    vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.'
                );

                progress.report({ message: 'Analysis complete!' });
                return result;
            });

            // Check if analysis succeeded
            if (result.status === 'failed') {
                Notifications.showError(result.error_message || 'Failed to analyze error');
                return;
            }

            if (!result.fixes || result.fixes.length === 0) {
                Notifications.showWarning('No fixes generated. The error might be too complex.');
                
                // Show root cause if available
                if (result.root_cause_analysis) {
                    this.showRootCause(result.root_cause_analysis);
                }
                return;
            }

            // Show fixes
            await this.showAndApplyFixes(result.fixes, result.root_cause_analysis);

        } catch (error: any) {
            Notifications.showError(`Error: ${error.message}`);
            console.error('Fix error command failed:', error);
        }
    }

    private async getErrorLog(): Promise<string | undefined> {
        // Try to get from terminal
        const terminal = vscode.window.activeTerminal;
        // (You can later read from terminal if you want)

        // For now, ask user to paste error
        const errorLog = await Notifications.showInputBox({
            prompt: 'Paste the error log',
            placeHolder: 'Traceback (most recent call last)...',
            ignoreFocusOut: true
            // removed: multiline: true as any
        });

        return errorLog;
    }

    private showRootCause(analysis: string): void {
        const panel = vscode.window.createWebviewPanel(
            'rootCauseAnalysis',
            'Root Cause Analysis',
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
                    h1 {
                        color: var(--vscode-textLink-foreground);
                    }
                    .analysis {
                        background: var(--vscode-editor-background);
                        padding: 15px;
                        border-radius: 5px;
                        line-height: 1.6;
                        white-space: pre-wrap;
                    }
                </style>
            </head>
            <body>
                <h1>🧠 Root Cause Analysis</h1>
                <div class="analysis">${this.escapeHtml(analysis)}</div>
            </body>
            </html>
        `;
    }

    private async showAndApplyFixes(
        fixes: FixSuggestion[],
        rootCause?: string
    ): Promise<void> {
        // Create quick pick items
        interface FixQuickPickItem extends vscode.QuickPickItem {
            fix: FixSuggestion;
        }

        const items: FixQuickPickItem[] = fixes.map((fix, index) => ({
            label: `$(tools) Fix ${index + 1}: ${fix.file_path}`,
            description: `Confidence: ${(fix.confidence * 100).toFixed(0)}%`,
            detail: fix.explanation,
            fix: fix
        }));

        // Show quick pick
        const selected = await Notifications.showQuickPick(items, {
            placeHolder: 'Select a fix to apply',
            ignoreFocusOut: true
        });

        if (!selected) {
            return;
        }

        // Preview diff
        await this.showDiff(selected.fix);

        // Confirm application
        const shouldApply = await Notifications.confirm(
            'Apply this fix to your code?'
        );

        if (!shouldApply) {
            return;
        }

        // Apply fix
        await this.applyFix(selected.fix);
    }

    private async showDiff(fix: FixSuggestion): Promise<void> {
        // Create temporary documents for diff
        const originalDoc = await vscode.workspace.openTextDocument({
            content: fix.original_snippet,
            language: this.detectLanguage(fix.file_path)
        });

        const fixedDoc = await vscode.workspace.openTextDocument({
            content: fix.new_snippet,
            language: this.detectLanguage(fix.file_path)
        });

        // Show diff
        await vscode.commands.executeCommand(
            'vscode.diff',
            originalDoc.uri,
            fixedDoc.uri,
            'Original ↔ Fixed'
        );
    }

    private async applyFix(fix: FixSuggestion): Promise<void> {
        try {
            const language = this.detectLanguage(fix.file_path);

            const result = await Notifications.showProgress('Applying fix...', async () => {
                return await this.client.applyFix(fix, language);
            });

            if (result.success) {
                Notifications.showInfo(`Fix applied successfully! (ID: ${result.fix_id})`);
                
                // Open the fixed file
                const doc = await vscode.workspace.openTextDocument(fix.file_path);
                await vscode.window.showTextDocument(doc);
            } else {
                Notifications.showError(`Failed to apply fix: ${result.message}`);
            }
        } catch (error: any) {
            Notifications.showError(`Error applying fix: ${error.message}`);
        }
    }

    private detectLanguage(filePath: string): string {
        if (filePath.endsWith('.py')) {
            return 'python';
        } else if (filePath.endsWith('.js') || filePath.endsWith('.jsx')) {
            return 'javascript';
        } else if (filePath.endsWith('.ts') || filePath.endsWith('.tsx')) {
            return 'typescript';
        }
        return 'python';
    }

    private escapeHtml(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}
