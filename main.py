from bot.main import TBot
import os
def main():
    new_bot = Bot(os.environ.get("TELEBOTTOKEN"))
    new_bot.start_bot()

    BOT.infinity_polling()
if __name__ == "__main__":
    main()