#!/usr/bin/env python

import requests
import sys
import time
import os
from datetime import datetime

URL = "http://100.124.128.57:8001"


# =========================
# VOZ (ESTÁVEL)
# =========================
def falar(texto):
    try:
        texto = str(texto)

        # limpeza forte (evita crash do espeak)
        texto = texto.replace('"', '')
        texto = texto.replace("'", '')
        texto = texto.replace("\n", " ")
        texto = texto.strip()

        if not texto:
            return

        os.system(
            f'espeak-ng -v pt-br -s 165 -a 200 "{texto}"'
        )

    except Exception as e:
        print("[ERRO VOZ]", e)


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
def saudacao_local():
    agora = datetime.now()

    hora = agora.hour
    data = agora.strftime("%d/%m/%Y")
    horario = agora.strftime("%H:%M")

    if hora < 12:
        periodo = "Bom dia"
    elif hora < 18:
        periodo = "Boa tarde"
    else:
        periodo = "Boa noite"

    return (
        f"{periodo}, hoje é dia {data} "
        f"e são {horario}. "
        f"No que posso ajudar hoje?"
    )


# =========================
# CONEXÃO COM SERVIDOR
# =========================
def conectar_servidor():
    while True:
        try:
            print("[•] Conectando ao servidor...")

            r = requests.post(
                URL,
                json={"msg": "__ping__"},
                timeout=5
            )

            if r.status_code != 200:
                raise Exception()

            print("    └── conexão estabelecida\n")

            print("══════════════════════════════")
            print("STATUS :: ONLINE\n")

            msg = saudacao_local()

            print("Sema:")
            print(msg)
            print()

            falar(msg)

            return True

        except requests.exceptions.ConnectionError:
            print("    └── servidor indisponível\n")

        except requests.exceptions.Timeout:
            print("    └── tempo de conexão excedido\n")

        except Exception:
            print("    └── erro inesperado\n")

        print("Tentando novamente em 3 segundos...\n")
        time.sleep(3)

        if input("Deseja continuar tentando? (Y/n): ").lower() == "n":
            print("Encerrando Sema...\n")
            sys.exit()


# =========================
# INÍCIO
# =========================
boot()
conectar_servidor()


# =========================
# LOOP PRINCIPAL
# =========================
while True:

    msg = input("Você: ")

    if msg.lower() == "sair":
        print("\nEncerrando Sema...\n")
        sys.exit()

    try:
        r = requests.post(URL, json={"msg": msg}, timeout=30)
        r.raise_for_status()

        texto = r.json().get("resposta", "")

        print(f"\nSema:\n{texto}\n")

        falar(texto)

    except requests.exceptions.ConnectionError:
        print("\n⚠ Conexão perdida.\n")
        conectar_servidor()

    except requests.exceptions.Timeout:
        print("\n⚠ Tempo excedido.\n")

    except Exception as e:
        print(f"\n⚠ Erro inesperado:\n{e}\n")