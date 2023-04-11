from pulsectl import Pulse

from src.enums.command_types import CommandTypes

from .utils import try_parse_int


class MenuOption:
    def __init__(self, name, description, command, icon):
        self.name = name
        self.description = description
        self.command = command
        self.icon = icon


class Application:
    def __init__(self, sink, name=None):
        self.sink = sink
        self.index = sink.index
        self.name = name or sink.name
        self.volume = sink.volumes if hasattr(sink, "volumes") else sink.volume


class Device:
    def __init__(self, card):
        self.card = card
        self.index = card.index
        self.name = card.name
        self.description = card.profile_active.description
        self.profile_active = card.profile_active
        self.profile_list = card.profile_list


class Profile:
    def __init__(self, profile, device):
        self.name = profile.name
        self.description = profile.description
        self.device = device.index


def get_options():
    return [
        MenuOption(
            name="Volume control",
            description="Change the volume of the system of applications",
            command=CommandTypes.VOLUME.value,
            icon="images/icon.png",
        ),
        MenuOption(
            name="Device profiles",
            description="Change the profile of the current device",
            command=CommandTypes.PROFILE.value,
            icon="images/device.png",
        ),
    ]


def get_system():
    with Pulse("ulauncher-volume-control") as pulse:
        sinks = pulse.sink_list()
        for sink in sinks:
            if sink.name == pulse.server_info().default_sink_name:
                return [Application(sink, "System")]

    return []


def get_playing_applications():
    applications = []
    with Pulse("ulauncher-volume-control") as pulse:
        applications = pulse.sink_input_list()
    return [Application(application) for application in applications]


def get_devices():
    devices = []
    with Pulse("ulauncher-volume-control") as pulse:
        devices = pulse.card_list()
    return [Device(device) for device in devices]


def get_device_profiles(devices, device_index):
    profiles = []
    device = list(
        filter(
            lambda dev: try_parse_int(device_index) == dev.index,
            map(lambda device: device.card, devices),
        )
    )[0]
    profiles = device.profile_list
    return [Profile(profile, device) for profile in profiles]


def set_device_profile(device, profile_id):
    cards = get_devices()
    card = list(
        filter(
            lambda card: device == card.index,
            map(lambda card: card.card, cards),
        )
    )[0]
    with Pulse("ulauncher-volume-control") as pulse:
        pulse.card_profile_set(card, profile_id)


def set_application_volume(app, volume):
    sinks = get_system()
    sinks += get_playing_applications()
    sink = list(
        filter(
            lambda sink: app.index == sink.index,
            map(lambda sink: sink.sink, sinks),
        )
    )[0]
    with Pulse("ulauncher-volume-control") as pulse:
        pulse.volume_set_all_chans(sink, int(volume) / 100)


def on_cancel(query):
    user_query = f"{' '.join(query.strip().split(' ')[:-1])}"
    return user_query if len(user_query) == 0 else f"{user_query} "


def filter_items(arr, search=None):
    if len(arr) == 0 or search is None:
        return arr

    if type(arr[0]) == MenuOption:
        return filter_options(arr, search)

    if type(arr[0]) == Application:
        return filter_apps(arr, search)

    if type(arr[0]) == Device:
        return filter_devices(arr, search)

    if type(arr[0]) == Profile:
        return filter_profiles(arr, search)


def filter_options(options, search):
    return list(
        filter(
            lambda option: option.name.lower().find(search.lower()) > -1
            or option.description.lower().find(search.lower()) > -1,
            options,
        )
    )


def filter_apps(apps, search):
    return list(
        filter(
            lambda app: app.name.lower().find(search.lower()) > -1
            or try_parse_int(search) == app.index,
            apps,
        )
    )


def filter_devices(devices, search):
    return list(
        filter(
            lambda device: device.name.lower().find(search.lower()) > -1
            or device.description.lower().find(search.lower()) > -1
            or try_parse_int(search) == device.index,
            devices,
        )
    )


def filter_profiles(profiles, search):
    return list(
        filter(
            lambda profile: profile.name.lower().find(search.lower()) > -1
            or profile.description.lower().find(search.lower()) > -1
            or try_parse_int(search) == profile.device,
            profiles,
        )
    )
