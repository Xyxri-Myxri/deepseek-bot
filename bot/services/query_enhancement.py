import logging
from openai import OpenAI, OpenAIError

from bot.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from bot.services.presets import get_enhancement_preset

client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)


async def enhance_query(original_query: str, user_context: str = "") -> str:
    """
    Улучшает пользовательский запрос для получения более качественного ответа
    
    Args:
        original_query: Исходный запрос пользователя
        user_context: Контекст пользователя (опционально)
    
    Returns:
        Улучшенный запрос или исходный, если оптимизация не удалась
    """
    enhancement_preset = get_enhancement_preset()
    
    # Формируем промпт для оптимизации
    enhancement_prompt = f"""
    {enhancement_preset}

    Исходный запрос пользователя: "{original_query}"

    {f"Контекст пользователя: {user_context}" if user_context else ""}

    Проанализируй запрос и улучши его, если это необходимо. Верни только улучшенный запрос без дополнительных объяснений.
    """

    try:
        logging.info(f"Enhancing query: '{original_query}'")
        
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": enhancement_prompt}],
            temperature=0.3,  # Низкая температура для более стабильных результатов
            max_tokens=500,   # Ограничиваем длину ответа
        )
        
        enhanced_query = completion.choices[0].message.content.strip()
        
        # Проверяем, что ответ не пустой и не слишком длинный
        if enhanced_query and len(enhanced_query) <= 1000:
            logging.info(f"Query enhanced successfully: '{enhanced_query}'")
            return enhanced_query
        else:
            logging.warning(f"Enhanced query too long or empty, using original: '{original_query}'")
            return original_query
            
    except (OpenAIError, Exception) as e:
        # В случае ошибки возвращаем исходный запрос
        logging.error(f"Query enhancement failed: {e}, using original: '{original_query}'")
        return original_query


async def should_enhance_query(query: str) -> bool:
    """
    Определяет, нуждается ли запрос в улучшении
    
    Args:
        query: Запрос пользователя
        
    Returns:
        True если запрос нуждается в улучшении
    """
    # Простые эвристики для определения необходимости улучшения
    short_queries = len(query.strip()) < 10
    vague_queries = any(word in query.lower() for word in [
        "помоги", "как", "что", "почему", "где", "когда", "кто", 
        "объясни", "расскажи", "покажи", "сделай", "напиши"
    ])
    unclear_queries = any(phrase in query.lower() for phrase in [
        "это", "то", "вот", "так", "как это", "что это", "помоги с"
    ])
    
    needs_enhancement = short_queries or vague_queries or unclear_queries
    logging.info(f"Query analysis - short: {short_queries}, vague: {vague_queries}, unclear: {unclear_queries}, needs enhancement: {needs_enhancement}")
    
    return needs_enhancement


async def get_query_analysis(query: str) -> dict:
    """
    Анализирует запрос и возвращает метаданные
    
    Args:
        query: Запрос пользователя
        
    Returns:
        Словарь с анализом запроса
    """
    analysis = {
        "length": len(query),
        "is_short": len(query.strip()) < 10,
        "has_question_words": any(word in query.lower() for word in [
            "что", "как", "почему", "где", "когда", "кто", "зачем"
        ]),
        "has_vague_terms": any(term in query.lower() for term in [
            "это", "то", "вот", "так", "помоги", "сделай"
        ]),
        "needs_enhancement": await should_enhance_query(query)
    }
    
    return analysis
