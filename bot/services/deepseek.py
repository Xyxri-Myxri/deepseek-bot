from openai import OpenAI, OpenAIError

from bot.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from bot.services.presets import get_preset_text

client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)


async def query_deepseek(prompt: str, preset_name: str = "default") -> str:
    """Отправляет запрос в OpenRouter с учетом пресета и строгих инструкций"""
    preset_text = get_preset_text(preset_name)
    full_prompt = f"{preset_text}\n\n{prompt}".strip()

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": full_prompt}],
        )
        return completion.choices[0].message.content

    except OpenAIError as e:
        return f"Ошибка API OpenRouter: {e}"

    except Exception as e:
        return f"Ошибка сети или соединения: {e}"
