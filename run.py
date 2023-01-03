from dotenv import load_dotenv
load_dotenv() # need to load environment variables before anything else
from general_walarus import bot
import os

def main():
    bot.run(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    main()