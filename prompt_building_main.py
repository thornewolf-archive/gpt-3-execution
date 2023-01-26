import logging

from prompt_building import logic
from utils import ChatHistory
from telegram import TelegramInterface

logging.basicConfig(
    level=logging.INFO + 1, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
logger.addHandler(logging.FileHandler("bot.log", mode="w"))


def main():
    try:
        logic.main_conversation_loop(ChatHistory(), TelegramInterface())
    except KeyboardInterrupt:
        logger.log(21, "Exiting bot...")


if __name__ == "__main__":
    logger.log(21, "Starting bot...")
    main()
