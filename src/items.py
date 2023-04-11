from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

from src.utils import try_parse_int

from .enums import CommandTypes, EventTypes

VOLUME_ICON = "images/icon.png"
DEVICE_ICON = "images/device.png"
CANCEL_ICON = "images/cancel.png"


def show_menu(options):
    return [
        ExtensionResultItem(
            icon=option.icon,
            name=option.name,
            description=option.description,
            on_enter=ExtensionCustomAction(
                {
                    "type": EventTypes.MENU.value,
                    "command": option.command,
                },
                keep_app_open=True,
            ),
        )
        for option in options
    ]


def show_devices(devices):
    return [
        ExtensionResultItem(
            icon=DEVICE_ICON,
            name=f"#{device.index} {device.name}",
            description=f"Active profile: {device.description}",
            on_enter=ExtensionCustomAction(
                {
                    "type": EventTypes.DEVICE.value,
                    "command": CommandTypes.PROFILE.value,
                    "device": device,
                },
                keep_app_open=True,
            ),
        )
        for device in devices
    ]


def show_device_profiles(profiles):
    return [
        ExtensionResultItem(
            icon=DEVICE_ICON,
            name=profile.name,
            description=profile.description,
            on_enter=ExtensionCustomAction(
                {
                    "type": EventTypes.PROFILE.value,
                    "device": profile.device,
                    "profile": profile.name,
                },
                keep_app_open=False,
            ),
        )
        for profile in profiles
    ]


def show_playing_applications(apps):
    return [
        ExtensionResultItem(
            icon=VOLUME_ICON,
            name=f"#{app.index} {app.name}",
            description=f"{app.volume}",
            on_enter=ExtensionCustomAction(
                {
                    "type": EventTypes.APPLICATION.value,
                    "command": CommandTypes.VOLUME.value,
                    "application": app,
                },
                keep_app_open=True,
            ),
        )
        for app in apps
    ]


def show_volume_selection(apps, volume=None):
    return [
        ExtensionResultItem(
            icon=VOLUME_ICON,
            name=f"Set {app.name} volume to {vol}%",
            description=f"{app.volume}",
            on_enter=ExtensionCustomAction(
                {
                    "type": EventTypes.VOLUME.value,
                    "application": app,
                    "volume": vol,
                },
                keep_app_open=False,
            ),
        )
        for vol in (
            [0, 50, 70, 100]
            if not type(try_parse_int(volume)) == int
            else [try_parse_int(volume)]
        )
        for app in apps
    ]


def cancel(query):
    return [
        ExtensionResultItem(
            icon=CANCEL_ICON,
            name="Cancel",
            on_enter=ExtensionCustomAction(
                {
                    "type": EventTypes.CANCEL.value,
                    "query": query,
                },
                keep_app_open=query.count(" ") > 1,
            ),
        )
    ]
