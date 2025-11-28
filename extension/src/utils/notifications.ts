/**
 * Notification Utilities
 * User-friendly notifications and progress indicators
 */

import * as vscode from 'vscode';

export class Notifications {
    public static showInfo(message: string): void {
        vscode.window.showInformationMessage(`rootCauseAI: ${message}`);
    }

    public static showWarning(message: string): void {
        vscode.window.showWarningMessage(`rootCauseAI: ${message}`);
    }

    public static showError(message: string): void {
        vscode.window.showErrorMessage(`rootCauseAI: ${message}`);
    }

    public static async showProgress<T>(
        title: string,
        task: (progress: vscode.Progress<{ message?: string; increment?: number }>) => Promise<T>
    ): Promise<T> {
        return vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: `rootCauseAI: ${title}`,
                cancellable: false
            },
            task
        );
    }

    public static async showQuickPick<T extends vscode.QuickPickItem>(
        items: T[],
        options: vscode.QuickPickOptions
    ): Promise<T | undefined> {
        return vscode.window.showQuickPick(items, options);
    }

    public static async showInputBox(options: vscode.InputBoxOptions): Promise<string | undefined> {
        return vscode.window.showInputBox(options);
    }

    public static async confirm(message: string): Promise<boolean> {
        const result = await vscode.window.showInformationMessage(
            `rootCauseAI: ${message}`,
            { modal: true },
            'Yes',
            'No'
        );
        return result === 'Yes';
    }
}
