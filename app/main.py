# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import redis, psycopg2, os, socket
app = FastAPI()

INSTANCE_ID = socket.gethostname()

# Конфигурация из переменных окружения
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)
CACHE_TIMEOUT = os.getenv("CACHE_TIMEOUT", 30)
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_NAME = os.getenv("POSTGRES_DB", "shop")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Модель для создания (входящие данные)
class ItemCreate(BaseModel):
    name: str

# Модель для ответа (что вернёт API)
class ItemResponse(BaseModel):
    id: int
    name: str
    instance_id: str
    use_cache: str

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.on_event("startup")
def on_startup():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name TEXT);")
    # Добавляем тестовые данные только если таблица пуста
    cur.execute("SELECT COUNT(*) FROM items;")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO items (name) VALUES ('Кофе'), ('Чай');")
    conn.commit()
    cur.close()
    conn.close()

# --- ЧТЕНИЕ (с кешем) ---
@app.get("/items", response_model=list[ItemResponse])
def get_items():
    try:
        cached = cache.get("items_list")
        if cached:
            cached_items = eval(cached)
            return [dict(item, instance_id=INSTANCE_ID, use_cache=str(True)) for item in cached_items]
    except:
        pass

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items;")
    items = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    try:
        cache.setex("items_list", CACHE_TIMEOUT, str(items))
    except:
        pass
    return [dict(item, instance_id=INSTANCE_ID, use_cache=str(False)) for item in items]

# --- СОЗДАНИЕ (без кеша, с инвалидацией) ---
@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # SQL-инъекция невозможна благодаря параметризованным запросам
    cur.execute("INSERT INTO items (name) VALUES (%s) RETURNING id;", (item.name,))
    new_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()

    # Сбрасываем кеш, чтобы новые данные появились при следующем GET-запросе
    try:
        cache.delete("items_list") 
    except:
        pass

    return {"id": new_id, "name": item.name, "instance_id": INSTANCE_ID, "use_cache": str(False)}

@app.delete("/items/{item_id}", response_model=ItemResponse)
def delete_item(item_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    # Проверяем, существует ли запись
    cur.execute("SELECT id, name FROM items WHERE id = %s;", (item_id,))
    item = cur.fetchone()
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Удаляем запись
    cur.execute("DELETE FROM items WHERE id = %s;", (item_id,))
    conn.commit()
    
    cur.close()
    conn.close()

    # Сбрасываем кеш, чтобы список обновился
    try:
        cache.delete("items_list")
    except:
        pass

    return {"id": item[0], "name": item[1], "instance_id": INSTANCE_ID, "use_cache": str(False)}