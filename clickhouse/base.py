import os

from clickhouse_driver import Client

CLICKHOUSE_HOST=os.getenv("CLICKHOUSE_HOST")
CLICKHOUSE_PORT=os.getenv("CLICKHOUSE_PORT")
CLICKHOUSE_USERNAME=os.getenv("CLICKHOUSE_USERNAME")
CLICKHOUSE_PASSWORD=os.getenv("CLICKHOUSE_PASSWORD")
CLICKHOUSE_DBNAME=os.getenv("CLICKHOUSE_DBNAME")

client = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, user=CLICKHOUSE_USERNAME, password=CLICKHOUSE_PASSWORD, database=CLICKHOUSE_DBNAME)

def update_schema():
    # 1) Читаем содержимое файла
    with open('./clickhouse/schema.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()

    # 2) Разбиваем на отдельные запросы по точке с запятой
    #    Однако учтите, что не всегда простой split(";") корректен,
    #    например, если внутри запроса встречаются комментарии или точки с запятой внутри строк.
    #    В простых случаях этого бывает достаточно.
    queries = [q.strip() for q in sql_script.split(';') if q.strip()]

    # 3) Выполняем каждый запрос
    for query in queries:
        # Если это запрос на создание/изменение таблицы и т.д. – просто execute
        # Если это SELECT и вы хотите результат, сохраните в переменную
        print(f"Executing query:\n{query}")
        result = client.execute(query)
        print("Result:", result)


update_schema()