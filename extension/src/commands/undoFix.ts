/**
 * Undo Fix Command
 * Reverts the last applied fix
 */

import * as vscode from 'vscode';
import { BackendClient } from '../utils/backendClient';
import { Notifications } from '../utils/notifications';

export class UndoFixCommand {
    constructor(private client: BackendClient) {}

    public async execute(): Promise<void> {
        try {
            const confirm = await Notifications.confirm('Undo the last fix?');
            
            if (!confirm) {
                return;
            }

            const result = await Notifications.showProgress('Undoing fix...', async () => {
                return await this.client.undoLastFix();
            });

            if (result.success) {
                Notifications.showInfo(result.message);
            } else {
                Notifications.showError(result.message);
            }
        } catch (error: any) {
            Notifications.showError(`Error: ${error.message}`);
        }
    }
}
