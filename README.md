
# DeepSeek Telegram Bot

Этот бот для Telegram использует **DeepSeek API** для обработки пользовательских запросов, поддерживает **хранение истории в PostgreSQL** и **Rate Limiting через Redis**.

---

## **📌 1. Установка зависимостей**
Перед запуском убедитесь, что у вас установлен **Docker** и **Docker Compose**.

Проверить установку можно командами:
```bash
docker -v
docker-compose -v
```

---

## **📌 2. Настройка переменных окружения**
Создайте файл `.env` в корневой папке проекта и добавьте в него переменные:

```ini
BOT_TOKEN=

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1

POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_PORT_OUT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

REDIS_HOST=
REDIS_PORT=
REDIS_PORT_OUT=
```

## **📌 3. Запуск проекта**
🔹 **Запускаем весь проект (бот, БД, Redis) одной командой:**
```bash
docker-compose up --build -d
```

🔹 **Проверяем логи бота:**
```bash
docker logs deepseek_bot -f
```
---

## **📌 4. Проверка работы**
🔹 **Убедитесь, что все контейнеры работают:**
```bash
docker ps
```
🔹 **Зайти в контейнер PostgreSQL и проверить данные:**
```bash
docker exec -it deepseek_postgres psql -U user -d deepseek
```
🔹 **Проверить, есть ли лимиты в Redis:**
```bash
docker exec -it deepseek_redis redis-cli
keys *
```
Если есть ключи `rate_limit:<user_id>`, значит **Rate Limiting работает**.

---

## **📌 5. Использование бота**
🔹 **После запуска можно взаимодействовать с ботом в Telegram:**  
1. **Отправьте текстовое сообщение** – бот обработает его через DeepSeek.  
2. **Команда `/history`** – бот покажет последние 5 запросов.  
3. **Rate Limiting:** Если отправлять слишком часто – **бот ограничит запросы** (Redis сбрасывает счетчик каждую минуту).  

---

## **📌 6. Остановка бота**
🔹 **Остановка всех контейнеров:**
```bash
docker-compose down
```
🔹 **Остановка только бота:**
```bash
docker-compose stop bot
```
🔹 **Запуск только бота:**
```bash
docker-compose start bot
```

---

## **✅ Итог**
🎯 **Теперь вы можете запустить Telegram-бота в один клик!** 🚀  
- ✅ **DeepSeek API интеграция**  
- ✅ **История запросов в PostgreSQL**  
- ✅ **Rate Limiting в Redis**  
- ✅ **Полностью Dockerized – легкий деплой**

Запускайте и тестируйте бота в Telegram! 📩  
