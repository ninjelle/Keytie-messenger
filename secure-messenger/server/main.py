from fastapi import FastAPI

app = FastAPI(title="Secure Messenger Relay")


@app.get("/health")
def health():
    """Проверка, что сервер жив."""
    return {"status": "ok"}
