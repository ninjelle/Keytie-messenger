from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Keytie Relay")

bundles = {}
mailboxes = {}


class Bundle(BaseModel):
    ik: str
    spk: str
    opk: str


class Envelope(BaseModel):
    sender: str
    ik_pub: Optional[str] = None
    ek_pub: Optional[str] = None
    dh_pub: str
    pn: int
    n: int
    ciphertext: str


@app.post("/register/{username}")
def register(username: str, bundle: Bundle):
    bundles[username] = bundle
    return {"status": "ok"}


@app.get("/bundle/{username}")
def get_bundle(username: str) -> Bundle:
    if username not in bundles:
        raise HTTPException(status_code=404, detail="пользователь не найден")
    return bundles[username]


@app.post("/send/{recipient}")
def send(recipient: str, envelope: Envelope):
    mailboxes.setdefault(recipient, []).append(envelope)
    return {"status": "ok"}


@app.get("/messages/{username}")
def get_messages(username: str) -> list[Envelope]:
    messages = mailboxes.get(username, [])
    mailboxes[username] = []
    return messages