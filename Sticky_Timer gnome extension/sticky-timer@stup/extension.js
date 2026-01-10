// file: extension.js

import St from 'gi://St';
import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

export default class StickyTimerExtension extends Extension {
    constructor(metadata) {
        super(metadata);
        this._label = null;
        this._timeout = null;
    }

    enable() {
        log('Sticky Timer: Enabling extension');
        this._label = new St.Label({
            text: "00:00",
            style_class: 'system-status-label',
            y_align: Clutter.ActorAlign.CENTER
        });
        Main.panel._centerBox.add_child(this._label);

        // Load stylesheet
        try {
            const cssProvider = new St.CssProvider();
            const cssPath = `${this.path}/stylesheet.css`;
            cssProvider.load_from_path(cssPath);
            this._label.get_style_context().add_provider(
                cssProvider,
                St.StyleProviderPriority.APPLICATION
            );
        } catch (e) {
            logError(e, 'Sticky Timer CSS Error');
        }

        // Update timer every second
        this._timeout = GLib.timeout_add_seconds(
            GLib.PRIORITY_DEFAULT, 1,
            () => {
                this._updateTimer();
                return GLib.SOURCE_CONTINUE;
            }
        );

        this._updateTimer();
    }

    _updateTimer() {
        try {
            const file = Gio.File.new_for_path('/tmp/sticky_timer.txt');
            if (!file.query_exists(null)) {
                this._label.text = "00:00";
                return;
            }

            const [success, content] = file.load_contents(null);
            if (!success) {
                this._label.text = "00:00";
                return;
            }

            const contentStr = new TextDecoder().decode(content);
            if (!contentStr.trim()) {
                this._label.text = "00:00";
                return;
            }

            const timer_data = JSON.parse(contentStr);
            if (timer_data.time && typeof timer_data.time === 'string') {
                this._label.text = timer_data.subject
                    ? `${timer_data.subject}: ${timer_data.time}`
                    : timer_data.time;
            } else {
                this._label.text = "00:00";
            }
        } catch (e) {
            logError(e, `Sticky Timer Extension Error: ${e.message}`);
            this._label.text = "Error";
        }
    }

    disable() {
        if (this._label) {
            Main.panel._centerBox.remove_child(this._label);
            this._label.destroy();
            this._label = null;
        }
        if (this._timeout) {
            GLib.source_remove(this._timeout);
            this._timeout = null;
        }
    }
}

