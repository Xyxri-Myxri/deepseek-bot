from openai import OpenAI
from bot.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

client = OpenAI(
    base_url=DEEPSEEK_BASE_URL,
    api_key=DEEPSEEK_API_KEY
)

async def query_deepseek(prompt: str) -> str:
    """Отправляет запрос в OpenRouter (DeepSeek) и получает ответ."""
    try:
        completion = client.chat.completions.create(
            extra_body={},
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )

        return completion.choices[0].message.content
    except Exception as e:
        return f"Ошибка при обращении к OpenRouter API: {str(e)}"
