import logging

from logic import read_and_respond_to_chats_forever
from utils import ChatHistory
from telegram import TelegramInterface

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    try:
        read_and_respond_to_chats_forever(ChatHistory(), TelegramInterface())
    except KeyboardInterrupt:
        logger.info("Exiting bot...")


if __name__ == "__main__":
    logger.info("Starting bot...")
    main()
