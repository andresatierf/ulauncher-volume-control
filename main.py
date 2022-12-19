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
    def on_event(self, event, extension):
        query = event.get_argument()

        if query.isnumeric():
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name=f"Set system volume to {query}",
                        on_enter=ExtensionCustomAction(
                            {
                                "vol": query,
                            },
                            keep_app_open=False,
                        ),
                    )
                ]
            )

        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Set system volume",
                    on_enter=HideWindowAction(),
                )
            ]
        )

        items = []
        # logger.info("preferences %s" % json.dumps(extension.preferences))
        for i in range(5):
            item_name = extension.preferences["item_name"]
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="%s %s" % (item_name, i),
                    description="Item description %s" % i,
                    on_enter=HideWindowAction(),
                )
            )

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {data.vol}%")


if __name__ == "__main__":
    VolumeControlExtension().run()
