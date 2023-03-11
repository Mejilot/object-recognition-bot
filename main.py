from bot.bot_class import TBot
import os


def main():
    new_bot = TBot(os.environ.get("TELEBOTTOKEN"))
    new_bot.start_bot()


if __name__ == "__main__":
    main()
