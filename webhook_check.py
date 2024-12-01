import requests

# Замените на ваш токен бота
BOT_TOKEN = "7967474690:AAE1AkydRFr-Xi-OOBRTv1pHkrrmVLYofVM"
WEBHOOK_URL = "https://nig-edit-bot.onrender.com/webhook"

# Базовый URL API Telegram
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_webhook_info():
    response = requests.get(f"{BASE_URL}/getWebhookInfo")
    if response.ok:
        print("Webhook Info:")
        print(response.json())
    else:
        print("Failed to get webhook info:", response.text)

def delete_webhook():
    response = requests.post(f"{BASE_URL}/deleteWebhook")
    if response.ok:
        print("Webhook deleted successfully.")
    else:
        print("Failed to delete webhook:", response.text)

def set_webhook():
    response = requests.post(f"{BASE_URL}/setWebhook", json={"url": WEBHOOK_URL})
    if response.ok:
        print("Webhook set successfully.")
    else:
        print("Failed to set webhook:", response.text)

if __name__ == "__main__":
    print("Checking current webhook status...")
    get_webhook_info()

    print("\nDeleting existing webhook (if any)...")
    delete_webhook()

    print("\nSetting new webhook...")
    set_webhook()

    print("\nRechecking webhook status...")
    get_webhook_info()
