from pulsectl import Pulse
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction


def getSystem():
    with Pulse("ulauncher-volume-control") as pulse:
        sinks = pulse.sink_list()
        for sink in sinks:
            if sink.name == pulse.server_info().default_sink_name:
                return sink

    return None


def getPlayingApplications():
    with Pulse("ulauncher-volume-control") as pulse:
        return pulse.sink_input_list()


def createEntries(apps, name, description, on_enter):
    entries = []
    for app in apps:
        entries.append(
            ExtensionResultItem(
                icon="images/icon.png",
                name=name(app),
                description=description(app),
                on_enter=on_enter(app),
            )
        )
    return entries


def getCleanName(app, system):
    return "System" if app.name == system.name else app.name


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

        if system:
            apps.insert(0, system)

        if not query:
            return RenderResultListAction(
                createEntries(
                    apps=apps,
                    name=lambda app: f"#{app.index} {getCleanName(app, system)}",
                    description=lambda app: f"{app.volume}",
                    on_enter=lambda app: SetUserQueryAction(
                        f"{event.get_keyword()} {getCleanName(app, system)} "
                    ),
                )
            )

        if query and query.isnumeric():
            volume = query
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name=f"Set {getCleanName(system, system)} volume to {volume}",
                        description=str(system.volume),
                        on_enter=ExtensionCustomAction(
                            {
                                "sink": system,
                                "volume": volume,
                            },
                            keep_app_open=False,
                        ),
                    )
                ]
            )

        application, *volume = query.split()
        apps = list(
            filter(
                lambda app: application.lower() in getCleanName(app, system).lower(),
                apps,
            )
        )

        if (
            list(
                filter(lambda app: getCleanName(app, system).lower() == "system", apps)
            )
            == []
        ):
            apps.append(system)

        if not volume:
            return RenderResultListAction(
                createEntries(
                    apps=apps,
                    name=lambda app: f"#{app.index} {getCleanName(app, system)}",
                    description=lambda app: str(app.volume),
                    on_enter=lambda app: SetUserQueryAction(
                        f"{event.get_keyword()} {getCleanName(app, system)} "
                    ),
                )
            )

        volume = volume.pop()
        return RenderResultListAction(
            createEntries(
                apps=apps,
                name=lambda app: f"Set {getCleanName(app, system)} volume to {volume}%",
                description=lambda app: str(app.volume),
                on_enter=lambda app: ExtensionCustomAction(
                    {
                        "sink": app,
                        "volume": volume,
                    },
                    keep_app_open=False,
                ),
            )
        )


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        sink = data["sink"]
        volume = data["volume"]
        with Pulse("ulauncher-volume-control") as pulse:
            pulse.volume_set_all_chans(sink, int(volume) / 100)


if __name__ == "__main__":
    VolumeControlExtension().run()
