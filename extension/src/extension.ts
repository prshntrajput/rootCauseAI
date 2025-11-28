/**
 * rootCauseAI VSCode Extension
 * Main entry point
 */

import * as vscode from 'vscode';
import { BackendClient } from './utils/backendClient';
import { Notifications } from './utils/notifications';
import { FixErrorCommand } from './commands/fixError';
import { ExplainErrorCommand } from './commands/explainError';
import { UndoFixCommand } from './commands/undoFix';
import { ShowHistoryCommand } from './commands/showHistory';
import { ShowStatsCommand } from './commands/showStats';

let backendClient: BackendClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('rootCauseAI extension is now active!');

    // Initialize backend client
    backendClient = new BackendClient();

    // Check backend health on startup
    checkBackendHealth();

    // Initialize commands
    const fixErrorCommand = new FixErrorCommand(backendClient);
    const explainErrorCommand = new ExplainErrorCommand(backendClient);
    const undoFixCommand = new UndoFixCommand(backendClient);
    const showHistoryCommand = new ShowHistoryCommand(backendClient);
    const showStatsCommand = new ShowStatsCommand(backendClient);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('rootcauseai.fixError', () => fixErrorCommand.execute())
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('rootcauseai.explainError', () => explainErrorCommand.execute())
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('rootcauseai.undoFix', () => undoFixCommand.execute())
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('rootcauseai.showHistory', () => showHistoryCommand.execute())
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('rootcauseai.showStats', () => showStatsCommand.execute())
    );

    // Show welcome message
    Notifications.showInfo('rootCauseAI is ready! 🚀');
}

async function checkBackendHealth(): Promise<void> {
    try {
        const isHealthy = await backendClient.checkHealth();
        
        if (!isHealthy) {
            const action = await vscode.window.showWarningMessage(
                'rootCauseAI backend is not running. Start it now?',
                'Start Backend',
                'Dismiss'
            );

            if (action === 'Start Backend') {
                showBackendInstructions();
            }
        }
    } catch (error) {
        // Silently fail - user will see error when they try to use commands
    }
}

function showBackendInstructions(): void {
    const panel = vscode.window.createWebviewPanel(
        'backendInstructions',
        'Start rootCauseAI Backend',
        vscode.ViewColumn.One,
        {}
    );

    panel.webview.html = `
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Start rootCauseAI Backend</h1>
            <p>Open a terminal and run:</p>
            <pre>de>cd /path/to/ai-error-fixer
source .venv/bin/activate
python backend/server.py</code></pre>
            <p>The backend will start at de>http://localhost:8000</code></p>
        </body>
        </html>
    `;
}

export function deactivate() {
    console.log('rootCauseAI extension is now deactivated');
}
