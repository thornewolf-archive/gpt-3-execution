from logic import read_and_respond_to_chats_forever
from utils import ChatHistory
from telegram import TelegramInterface


def main():
    read_and_respond_to_chats_forever(ChatHistory(), TelegramInterface())


if __name__ == "__main__":
    print("Starting bot...")
    main()
