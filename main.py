import requests
import time
import json
from telegram import Bot

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

wallets = config["wallets"]
api_key = config["api_key"]
check_interval = config["check_interval"]
telegram_bot_token = config["telegram_bot_token"]
telegram_chat_id = config["telegram_chat_id"]
etherscan_url = "https://api.etherscan.io/api"

# Init bot
bot = Bot(token=telegram_bot_token)

def get_transactions(address, api_key):
    url = f"{etherscan_url}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "1":
        return data["result"]
    else:
        print(f"Error fetching transactions for {address}: {data['message']}")
        return []

def send_telegram_message(chat_id, text):
    bot.send_message(chat_id=chat_id, text=text)

def monitor_transactions(wallets, api_key, chat_id):
    known_transactions = {address: set() for address in wallets}
    while True:
        for address, name in wallets.items():
            transactions = get_transactions(address, api_key)
            for tx in transactions:
                if tx['hash'] not in known_transactions[address]:
                    known_transactions[address].add(tx['hash'])
                    value_in_ether = int(tx['value']) / 10**18
                    message = (
                        f"New transaction detected for {name} ({address}):\n"
                        f"From: {tx['from']}\n"
                        f"To: {tx['to']}\n"
                        f"Value: {value_in_ether} ETH\n"
                        f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(tx['timeStamp'])))}"
                    )
                    send_telegram_message(chat_id, message)
                    print(message)
        time.sleep(check_interval)

monitor_transactions(wallets, api_key, telegram_chat_id)
# 