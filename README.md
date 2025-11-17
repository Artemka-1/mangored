
# Инструкции

1. Создайте Atlas MongoDB кластер и пользователя. Получите connection string и установите переменную окружения:
   ```bash
   export MONGO_URI="mongodb+srv://USER:PASS@cluster0.mongodb.net/mydb"

   
2. (Опционально) Запустите Redis (локально или облачно). Установите:

export REDIS_URL="redis://localhost:6379/0

3. Установите зависимости:

pip install -r requirements.txt

4. Загрузите данные в базу:

MONGO_URI="..." python load_data.py --authors authors.json --quotes qoutes.json

5. Запустите интерактивный CLI:

MONGO_URI="..." REDIS_URL="..." python search_cli.py
