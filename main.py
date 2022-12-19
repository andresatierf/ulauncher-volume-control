import os
import subprocess
import re
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction



def getPlayingApplications():
    output = str(subprocess.check_output("pactl list sink-inputs", shell=True))
    names = re.findall('application.name = "(.+?)"', output)
    sinks = re.findall("Sink Input #(\d+)", output)
    vols = re.findall("Volume: (.+?)\\\\n", output)

    return [
        {"name": name, "sink-input": sink, "vol": vol}
        for name, sink, vol in zip(names, sinks, vols)
    ]


def createEntries(apps, action, entry=None):
    entries = []
    for app in apps:
        entries.append(
            ExtensionResultItem(
                icon="images/icon.png",
                name=app["name"] if not entry else entry(app),
                description=app["vol"],
                on_enter=action(app),
            )
        )
    return entries


class VolumeControlExtension(Extension):
    def __init__(self):
        super(VolumeControlExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        apps = getPlayingApplications()
        query = event.get_argument()

        if not query:
            return RenderResultListAction(
                createEntries(
                    apps=apps,
                    action=lambda app: SetUserQueryAction(
                        f'{event.get_keyword()} {app["name"]}'
                    ),
                )
            )

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
                            keep_app_open=True,
                        ),
                    )
                ]
            )

        application, *volume = query.split()
        for app in apps:
            print(application, app)
            if application.lower() not in app["name"].lower():
                apps.pop(app)

        if not volume:
            return RenderResultListAction(
                createEntries(
                    apps=apps,
                    action=lambda app: SetUserQueryAction(
                        f'{event.get_keyword()} {app["name"]}'
                    ),
                )
            )

        volume = volume.pop()
        return RenderResultListAction(
            createEntries(
                apps=apps,
                action=lambda app: ExtensionCustomAction(
                    {
                        "cmd": "set-sink-input-volume",
                        "sink": app["sink-input"],
                        "vol": volume,
                    },
                    keep_app_open=False,
                ),
                entry=lambda app: f"Set {app['name']} volume to {volume}%",
            )
        )


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        print(data)
        os.system(f"pactl {data['cmd']} {data['sink']} {data['vol']}%")


if __name__ == "__main__":
    VolumeControlExtension().run()
