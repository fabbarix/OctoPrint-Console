# coding=utf-8
from __future__ import absolute_import

import time, asyncio, websockets
import octoprint.plugin

from .server.token import token
from .server.ws_server import ShellServer

class OctoConsolePlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin
):

    ##~~ After Startup
    def on_after_startup(self):
        self._logger.info(f"OctoPrint Console Starting - Token: {token()}")
        self.server = ShellServer(self._logger)
        self.server.start()
        self._logger.info(f"OctoPrint Console Started")

    def on_shutdown(self):
        self._logger.info(f"OctoPrint Stopping WebSockets")
        self.server.stop()

    def on_event(self, event, payload):
        self._logger.info(f"{event} Payload: {str(payload)}")

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    ##~~ AssetPlugin mixin
    def get_template_vars(self):
            return dict(
                ws_port=6969,
                ws_token=token()
            )

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": [
                "js/xterm.js",
                "js/xterm-addon-attach.js",
                "js/xterm-addon-fit.js",
                "js/octoconsole.js"
            ],
            "css": [
                "css/octoconsole.css",
                "css/xterm.css",
            ]
        }

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "octoconsole": {
                "displayName": "OctoPrint Console",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "fabbari",
                "repo": "OctoPrint-Console",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/fabbarix/OctoPrint-Console/archive/refs/tags/v{target_version}.zip",
            }
        }

__plugin_pythoncompat__ = ">=3.0,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OctoConsolePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
