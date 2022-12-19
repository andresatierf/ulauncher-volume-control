import json
import logging
from time import sleep
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)


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
                            {"new_name": "Item %s was clicked"}, keep_app_open=False
                        ),
                    )
                ]
            )

        items = []
        logger.info("preferences %s" % json.dumps(extension.preferences))
        for i in range(5):
            item_name = extension.preferences["item_name"]
            data = {"new_name": "%s %s was clicked" % (item_name, i)}
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="%s %s" % (item_name, i),
                    description="Item description %s" % i,
                    on_enter=ExtensionCustomAction(
                        {"new_name": "Item %s was clicked"}, keep_app_open=False
                    ),
                )
            )

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=data["new_name"],
                    on_enter=HideWindowAction(),
                )
            ]
        )


if __name__ == "__main__":
    VolumeControlExtension().run()
