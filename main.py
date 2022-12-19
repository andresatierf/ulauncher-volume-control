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


def getSystem():
    output = str(subprocess.check_output("pactl list sinks", shell=True))
    sinks = re.findall("Sink #(\d+)\\\\n\\\\tState: RUNNING", output)
    vols = re.findall("State: RUNNING.*?Volume: (.+?)\\\\n", output)
    return {
        "name": "System",
        "sink": sinks.pop(0),
        "vol": vols.pop(0),
        "cmd": "set-sink-volume",
    }


def getPlayingApplications():
    output = str(subprocess.check_output("pactl list sink-inputs", shell=True))
    names = re.findall('application.name = "(.+?)"', output)
    sinks = re.findall("Sink Input #(\d+)", output)
    vols = re.findall("Volume: (.+?)\\\\n", output)

    return [
        {"name": name, "sink": sink, "vol": vol, "cmd": "set-sink-input-volume"}
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
        system = getSystem()
        apps = getPlayingApplications()
        query = event.get_argument()

        apps.insert(0, system)
        if not query:
            return RenderResultListAction(
                createEntries(
                    apps=apps,
                    action=lambda app: SetUserQueryAction(
                        f'{event.get_keyword()} {app["name"]} '
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
        for index, app in enumerate(apps):
            if application.lower() not in app["name"].lower():
                if app["name"].lower() == "system":
                    apps.append(
                        apps.pop(
                            list(map(lambda app: app["name"].lower(), apps)).index(
                                "system"
                            )
                        )
                    )
                    continue

                apps.pop(index)

        if not volume:
            return RenderResultListAction(
                createEntries(
                    apps=apps,
                    action=lambda app: SetUserQueryAction(
                        f'{event.get_keyword()} {app["name"]} '
                    ),
                )
            )

        volume = volume.pop()
        return RenderResultListAction(
            createEntries(
                apps=apps,
                action=lambda app: ExtensionCustomAction(
                    {
                        "cmd": app["cmd"],
                        "sink": app["sink"],
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
        os.system(f"pactl {data['cmd']} {data['sink']} {data['vol']}%")


if __name__ == "__main__":
    VolumeControlExtension().run()
