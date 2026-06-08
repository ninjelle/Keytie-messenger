import json
import sqlite3
from contextlib import closing
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Keytie Relay")

DB = "keytie.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_db()) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS bundles (username TEXT PRIMARY KEY, ik TEXT, spk TEXT, opk TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, recipient TEXT, payload TEXT)"
        )
        conn.commit()


init_db()


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
    group: Optional[str] = None


@app.post("/register/{username}")
def register(username: str, bundle: Bundle):
    with closing(get_db()) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO bundles (username, ik, spk, opk) VALUES (?, ?, ?, ?)",
            (username, bundle.ik, bundle.spk, bundle.opk),
        )
        conn.commit()
    return {"status": "ok"}


@app.get("/bundle/{username}")
def get_bundle(username: str) -> Bundle:
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT ik, spk, opk FROM bundles WHERE username = ?", (username,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="пользователь не найден")
    return Bundle(ik=row["ik"], spk=row["spk"], opk=row["opk"])


@app.post("/send/{recipient}")
def send(recipient: str, envelope: Envelope):
    with closing(get_db()) as conn:
        conn.execute(
            "INSERT INTO messages (recipient, payload) VALUES (?, ?)",
            (recipient, envelope.model_dump_json()),
        )
        conn.commit()
    return {"status": "ok"}


@app.get("/messages/{username}")
def get_messages(username: str) -> list[Envelope]:
    with closing(get_db()) as conn:
        rows = conn.execute(
            "SELECT id, payload FROM messages WHERE recipient = ?", (username,)
        ).fetchall()
        ids = [row["id"] for row in rows]
        if ids:
            conn.executemany("DELETE FROM messages WHERE id = ?", [(i,) for i in ids])
            conn.commit()
    return [Envelope(**json.loads(row["payload"])) for row in rows]