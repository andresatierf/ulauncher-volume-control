from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

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
    filter_items,
    get_device_profiles,
    get_options,
    get_devices,
    get_system,
    get_playing_applications,
    on_cancel,
    set_device_profile,
    set_application_volume,
)
from src.utils import try_parse_int


class VolumeControlExtension(Extension):
    def __init__(self):
        super(VolumeControlExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def render_option_menu(self, query, argument):
        options = get_options()
        options = filter_items(options, argument)

        items = show_menu(options)
        items += cancel(query)

        return RenderResultListAction(items)

    def render_application_menu(self, apps, query, components=None):
        apps = filter_items(apps, components)

        items = show_playing_applications(apps)
        items += cancel(query)

        return RenderResultListAction(items)

    def render_volume_selection_menu(self, apps, query, app_id, volume=None):
        apps = filter_items(apps, app_id)

        items = show_volume_selection(apps, volume)
        items += cancel(query)

        return RenderResultListAction(items)

    def render_device_menu(self, devices, query, components=None):
        devices = filter_items(devices, components)

        items = show_devices(devices)
        items += cancel(query)

        return RenderResultListAction(items)

    def render_profile_menu(self, devices, query, device_id, profile_id=None):
        profiles = get_device_profiles(devices, device_id)
        profiles = filter_items(profiles, profile_id)

        items = show_device_profiles(profiles)
        items += cancel(query)

        return RenderResultListAction(items)

    def on_event(self, event, extension):
        query = event.get_query()
        argument = event.get_argument()

        if not argument:
            return self.render_option_menu(query, argument)

        command, *components = argument.split()
        components = " ".join(components).strip()

        if command == CommandTypes.VOLUME.value:
            apps = get_system()
            apps += get_playing_applications()

            if not components:
                return self.render_application_menu(apps, query)

            application_id, *volume = components.split()
            volume = " ".join(volume).strip()

            is_valid_application = try_parse_int(application_id) in list(
                map(lambda app: app.index, apps)
            )
            if is_valid_application:
                return self.render_volume_selection_menu(
                    apps, query, application_id, volume
                )

            return self.render_application_menu(apps, query, components)

        if command == CommandTypes.PROFILE.value:
            devices = get_devices()

            if not components:
                return self.render_device_menu(devices, query, components)

            device_id, *profile_id = components.split()
            profile_id = " ".join(profile_id)

            is_valid_device = try_parse_int(device_id) in list(
                map(lambda device: device.index, devices)
            )
            if is_valid_device:
                return self.render_profile_menu(devices, query, device_id, profile_id)

            return self.render_device_menu(devices, query, components)

        return self.render_option_menu(query, argument)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        keyword = extension.preferences["keyword"]
        data = event.get_data()
        type = data.get("type")

        if type == EventTypes.MENU.value:
            command = data.get("command")
            return SetUserQueryAction(f"{keyword} {command} ")

        if type == EventTypes.APPLICATION.value:
            command = data.get("command")
            app = data.get("application")
            return SetUserQueryAction(f"{keyword} {command} {app.index} ")

        if type == EventTypes.VOLUME.value:
            app = data.get("application")
            volume = data.get("volume")
            return set_application_volume(app, volume)

        if type == EventTypes.DEVICE.value:
            command = data.get("command")
            device = data.get("device")
            return SetUserQueryAction(f"{keyword} {command} {device.index} ")

        if type == EventTypes.PROFILE.value:
            device = data.get("device")
            profile = data.get("profile")
            return set_device_profile(device, profile)

        if type == EventTypes.CANCEL.value:
            query = data.get("query")
            user_query = on_cancel(query)
            return SetUserQueryAction(user_query)

        return DoNothingAction()


if __name__ == "__main__":
    VolumeControlExtension().run()
