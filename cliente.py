#!/usr/bin/env python

import asyncio
import websockets
import json
import requests
import sys
from datetime import datetime

SERVER_URL = "http://100.124.128.57:8001"
API_KEY = "SUA_API_KEY"

WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"


# =========================
# BOOT
# =========================
def boot():
    print("""
══════════════════════════════
            S E M A
══════════════════════════════
""")


# =========================
# SAUDAÇÃO LOCAL
# =========================
def saudacao():
    agora = datetime.now()

    if agora.hour < 12:
        return "Bom dia"
    elif agora.hour < 18:
        return "Boa tarde"
    return "Boa noite"


# =========================
# BUSCA CONTEXTO NO SERVIDOR
# =========================
def get_contexto(msg):
    r = requests.post(SERVER_URL, json={"msg": msg}, timeout=10)
    return r.json().get("contexto", "")


# =========================
# REALTIME
# =========================
async def run():

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    async with websockets.connect(WS_URL, extra_headers=headers) as ws:

        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text"],
                "instructions": "Você é Sema, assistente pessoal inteligente e amigável."
            }
        }))

        print("Sema:", saudacao())

        while True:

            msg = input("Você: ")

            if msg.lower() == "sair":
                sys.exit()

            # pega memória do servidor
            contexto = get_contexto(msg)

            await ws.send(json.dumps({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "system",
                    "content": [{
                        "type": "input_text",
                        "text": contexto
                    }]
                }
            }))

            await ws.send(json.dumps({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": msg
                    }]
                }
            }))

            await ws.send(json.dumps({
                "type": "response.create"
            }))

            resposta = ""

            while True:
                data = json.loads(await ws.recv())

                if data.get("type") == "response.output_text.delta":
                    print(data.get("delta", ""), end="", flush=True)
                    resposta += data.get("delta", "")

                if data.get("type") == "response.done":
                    print("\n")
                    break


boot()
asyncio.run(run())