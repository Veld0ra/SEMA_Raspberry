#!/usr/bin/env python

import sys
import asyncio
import json
import base64
import websockets
import sounddevice as sd
import numpy as np
from datetime import datetime

# =========================
# CONFIG REALTIME
# =========================
API_KEY = "SUA_API_KEY_AQUI"
URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"


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
# SAUDAÇÃO
# =========================
def saudacao_local():
    agora = datetime.now()

    if agora.hour < 12:
        periodo = "Bom dia"
    elif agora.hour < 18:
        periodo = "Boa tarde"
    else:
        periodo = "Boa noite"

    return (
        f"{periodo}, hoje é dia {agora.strftime('%d/%m/%Y')} "
        f"e são {agora.strftime('%H:%M')}. "
        f"No que posso ajudar hoje?"
    )


# =========================
# TOCAR ÁUDIO (REALTIME)
# =========================
def tocar_audio(base64_audio):
    audio_bytes = base64.b64decode(base64_audio)

    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

    sd.play(audio_array, samplerate=24000)
    sd.wait()


# =========================
# REALTIME CLIENT
# =========================
async def realtime():

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    async with websockets.connect(
        URL,
        additional_headers=headers,
        ping_interval=20,
        ping_timeout=20
    ) as ws:

        # sessão com VOZ ATIVADA
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],  # 🔥 AQUI ESTÁ A MÁGICA
                "voice": "alloy",  # voz humana da OpenAI
                "instructions": "Você é a SEMA, uma assistente inteligente, amigável e direta."
            }
        }))

        print("Sema:")
        print(saudacao_local())
        print()

        # fala saudação (texto ainda opcional)
        print("(voz será gerada pela API)")

        while True:

            msg = input("Você: ")

            if msg.lower() == "sair":
                print("\nEncerrando Sema...\n")
                sys.exit()

            try:
                # envia mensagem
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

                # pede resposta
                await ws.send(json.dumps({
                    "type": "response.create"
                }))

                resposta_texto = ""

                # recebe streaming (texto + áudio)
                while True:
                    data = json.loads(await ws.recv())
                    tipo = data.get("type")

                    # texto opcional (debug)
                    if tipo == "response.output_text.delta":
                        resposta_texto += data.get("delta", "")
                        print(data.get("delta", ""), end="", flush=True)

                    # áudio vindo da OpenAI
                    elif tipo == "response.audio.delta":
                        audio = data.get("delta")
                        tocar_audio(audio)

                    elif tipo == "response.done":
                        print("\n")
                        break

            except Exception as e:
                print(f"\n⚠ Erro Realtime Audio:\n{e}\n")
                break


# =========================
# INÍCIO
# =========================
boot()
asyncio.run(realtime())