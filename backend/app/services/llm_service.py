import httpx
import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
YANDEX_MODEL = os.getenv("YANDEX_MODEL", "yandexgpt/latest")  # универсальный вариант
YANDEX_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

async def ask_yandex_gpt(prompt: str) -> str:
    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        return "Ошибка: не настроены API-ключ или folder_id"

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_MODEL}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 500
        },
        "messages": [
            {"role": "system", "text": "Ты — Джарвис, персональный AI-ассистент по формированию привычек. Отвечай кратко, по делу, поддерживающе."},
            {"role": "user", "text": prompt}
        ]
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(YANDEX_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            # Поле ответа может быть "text" или "content" — проверим оба
            message = data["result"]["alternatives"][0]["message"]
            return message.get("text", message.get("content", "Нет текста в ответе"))
        except httpx.HTTPStatusError as e:
            print(f"YandexGPT error: {e.response.status_code}")
            print(e.response.text)  # покажет детали
            return "Извини, не удалось получить ответ от AI. Попробуй позже."
        except Exception as e:
            print(f"YandexGPT error: {e}")
            return "Извини, не удалось получить ответ от AI. Попробуй позже."