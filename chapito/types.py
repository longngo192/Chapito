from enum import Enum


class OsType(Enum):
    UNKNOWN = 0
    WINDOWS = 1
    LINUX = 2
    MACOS = 3


class Chatbot(Enum):
    GROK = "grok"
    MISTRAL = "mistral"
