from enum import Enum


class EventTypes(Enum):
    MENU = "menu"
    DEVICE = "device"
    VOLUME = "volume"
    APPS = "apps"
    PROFILE = "profile"
    CANCEL = "cancel"
