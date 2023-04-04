from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

from pulsectl import Pulse

from src.enums import EventTypes, CommandTypes
from src.items import (
    cancel,
    show_device_profiles,
    show_menu,
    show_playing_applications,
    show_devices,
    show_volume_selection,
)
from src.functions import (
    get_device_profiles,
    get_options,
    get_devices,
    get_system,
    get_playing_applications,
    filter_apps,
    set_device_profile,
    set_application_volume,
)


class VolumeControlExtension(Extension):
    def __init__(self):
        super(VolumeControlExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        keyword = event.get_keyword()
        argument = event.get_argument()

        if not argument:
            options = get_options()

            items = show_menu(options)
            items += cancel()

            return RenderResultListAction(items)

        command, *components = argument.split()

        if command == CommandTypes.VOLUME.value:
            apps = get_system()
            apps += get_playing_applications()

            if components:
                apps = filter_apps(apps, components[0])

            if len(components) > 1:
                volume = int(components[1]) if len(components) > 1 else None

                items = show_volume_selection(apps, volume)
                items += cancel()

                return RenderResultListAction(items)

            items = show_playing_applications(apps)
            items += cancel()

            return RenderResultListAction(items)

        if command == CommandTypes.PROFILE.value:
            if components:
                profiles = get_device_profiles(int(components[0]))

                items = show_device_profiles(profiles)
                items += cancel()

                return RenderResultListAction(items)

            devices = get_devices()

            items = show_devices(devices)
            items += cancel()

            return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        keyword = extension.preferences["keyword"]
        data = event.get_data()
        type = data.get("type")

        if type == EventTypes.MENU.value:
            # show new menu
            command = data.get("command")
            print(command)
            return SetUserQueryAction(f"{keyword} {command} ")

        if type == EventTypes.APPS.value:
            # select app
            command = data.get("command")
            app = data.get("application")
            return SetUserQueryAction(f"{keyword} {command} {app.index} ")

        if type == EventTypes.VOLUME.value:
            app = data.get("application")
            volume = data.get("volume")
            return set_application_volume(app, volume)

        if type == EventTypes.DEVICE.value:
            # show device profiles
            command = data.get("command")
            device = data.get("device")
            return SetUserQueryAction(f"{keyword} {command} {device.index}")

        if type == EventTypes.PROFILE.value:
            # select profile
            device = data.get("device")
            profile = data.get("profile")
            print(f"{device}, {profile}")
            return set_device_profile(device, profile)

        if type == EventTypes.CANCEL.value:
            return SetUserQueryAction("")

        return DoNothingAction()


if __name__ == "__main__":
    VolumeControlExtension().run()
