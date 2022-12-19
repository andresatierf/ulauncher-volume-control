# import json
# import logging
# from time import sleep
import os
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

# logger = logging.getLogger(__name__)


class VolumeControlExtension(Extension):
    def __init__(self):
        super(VolumeControlExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def getApps(self):
        os.system("pactl list sink-inputs")
        return [{"name": "spotify", "sink-input": "6"}]

    def on_event(self, event, extension):
        apps = getApps()

        query = event.get_argument()

        if query and query.isnumeric():
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name=f"Set system volume to {query}",
                        on_enter=ExtensionCustomAction(
                            {
                                "cmd": "set-sink-volume",
                                "sink": "@DEFAULT_SINK@",
                                "vol": query,
                            },
                            keep_app_open=False,
                        ),
                    )
                ]
            )

        items = []
        for app in apps:
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=app["name"],
                    on_enter=ExtensionCustomAction(
                        {"cmd": "set-sink-input-volume", "sink": app["sink-input"], "app": query.split()[1]}
                    ),
                )
            )

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        os.system(f"pactl {data['cmd']} {data['sink']} {data['vol']}%")


if __name__ == "__main__":
    VolumeControlExtension().run()
