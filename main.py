from proxy_chat.config import Config
from proxy_chat import grok_chat, mistral_chat
from proxy_chat.proxy import init_proxy
from proxy_chat.types import Chatbot


def main():
    config = Config()

    if config.chatbot == Chatbot.GROK:
        driver = grok_chat.initialize_driver(config)
        init_proxy(driver, grok_chat.send_request_and_get_response)

    if config.chatbot == Chatbot.MISTRAL:
        driver = mistral_chat.initialize_driver(config)
        init_proxy(driver, mistral_chat.send_request_and_get_response)


if __name__ == "__main__":
    main()
