import configparser
import argparse
from enum import Enum
import logging

from chapito.tools.log import setup_logging_verbosity
from chapito.types import Chatbot

DEFAULT_CONFIG_PATH: str = "config.ini"
DEFAULT_USE_BROWSER_PROFILE: bool = True
DEFAULT_BROWSER_PROFILE_PATH: str = "browser_profile"
DEFAULT_BROWSER_USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
DEFAULT_VERBOSITY: int = 1
DEFAULT_CHATBOT: Chatbot = Chatbot.GROK


class Config:
    config_path: str = DEFAULT_CONFIG_PATH
    use_browser_profile: bool = DEFAULT_USE_BROWSER_PROFILE
    browser_profile_path: str = DEFAULT_BROWSER_PROFILE_PATH
    browser_user_agent: str = DEFAULT_BROWSER_USER_AGENT
    verbosity: int = DEFAULT_VERBOSITY
    chatbot: Chatbot = DEFAULT_CHATBOT

    def __init__(self):
        logging.debug("Initializing config...")
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--config", type=str, help="Path to the config file (default: config.ini)", default=DEFAULT_CONFIG_PATH
        )
        parser.add_argument("--chatbot", type=str, help="Chatbot to connect to (available: grok, mistral)")
        parser.add_argument("--use-browser-profile", action="store_true", help="Use a browser profile")
        parser.add_argument("--profile-path", type=str, help="Path to the browser profile")
        parser.add_argument("--user-agent", type=str, help="User agent to use")
        parser.add_argument("--verbosity", type=int, help="User agent to use")
        args = parser.parse_args()
        self.config_path = args.config or DEFAULT_CONFIG_PATH
        config = configparser.ConfigParser()
        config.read(self.config_path)

        self.verbosity = args.verbosity or config.getint("DEFAULT", "verbosity", fallback=DEFAULT_VERBOSITY)
        setup_logging_verbosity(self.verbosity)
        self.use_browser_profile = args.use_browser_profile or config.getboolean(
            "DEFAULT", "use_browser_profile", fallback=DEFAULT_USE_BROWSER_PROFILE
        )
        self.browser_profile_path = args.profile_path or config.get(
            "DEFAULT", "browser_profile_path", fallback=DEFAULT_BROWSER_PROFILE_PATH
        )
        self.browser_user_agent = args.user_agent or config.get(
            "DEFAULT", "browser_user_agent", fallback=DEFAULT_BROWSER_USER_AGENT
        )
        chatbot_str = args.chatbot or config.get("DEFAULT", "chatbot", fallback=DEFAULT_CHATBOT)
        try:
            chatbot = Chatbot(chatbot_str)
        except ValueError as e:
            logging.error(f"Invalid chatbot specified: {chatbot_str}")
            chatbot = DEFAULT_CHATBOT

        self.chatbot = Chatbot(chatbot)

        logging.debug(f"Config initialized: {self.__dict__}")
