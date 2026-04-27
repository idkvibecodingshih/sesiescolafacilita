import flask
import flask_cors
import json
from openai import OpenAI
import os
import sqlite3


# =========================
# DATABASE
# =========================

def initialize_database():
    conn = sqlite3.connect("accounts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

initialize_database()


# =========================
# IA
# =========================

ENV_API_KEY = os.getenv("API_KEY")

class IA:
    def __init__(self, base_url, api_key):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        self.memoria = [
            {
                "role": "system",
                "content": "Você é Allen Dev, especialista em Roblox Studio e Luau. Ajude apenas com desenvolvimento legítimo."
            }
        ]

    def call(self, pergunta: str):
        try:
            self.memoria.append({
                "role": "user",
                "content": pergunta
            })

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0,
                messages=self.memoria
            )

            resposta = response.choices[0].message.content

            self.memoria.append({
                "role": "assistant",
                "content": resposta
            })

            return resposta

        except Exception as e:
            print("ERRO NA IA:", e)
            return "Erro ao processar a resposta da IA."


IA_instance = IA(
    base_url="https://api.groq.com/openai/v1",
    api_key=ENV_API_KEY
)


# =========================
# APP + CORS FIX
# =========================

app = flask.Flask(__name__)

flask_cors.CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# 🔥 CORREÇÃO PRINCIPAL DO CORS (preflight)
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


# =========================
# ROUTES
# =========================

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if flask.request.method == "OPTIONS":
        return "", 200

    data = flask.request.get_json()

    if not data or "question" not in data:
        return json.dumps({
            "status": "error",
            "message": "Pergunta não enviada."
        }), 400

    print("Received question:", data)

    resposta = IA_instance.call(data["question"])

    return json.dumps({
        "status": "success",
        "message": resposta
    }), 200


# =========================
# CADASTRO
# =========================

@app.route("/system/cadastro", methods=["POST", "OPTIONS"])
def cadastro():
    if flask.request.method == "OPTIONS":
        return "", 200

    data = flask.request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return json.dumps({
            "status": "error",
            "message": "Email e senha são obrigatórios."
        }), 400

    conn = sqlite3.connect("accounts.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO accounts (email, password) VALUES (?, ?)",
            (email, password)
        )
        conn.commit()

        return json.dumps({
            "status": "success",
            "message": "Conta criada com sucesso."
        }), 201

    except sqlite3.IntegrityError:
        return json.dumps({
            "status": "error",
            "message": "Email já cadastrado."
        }), 409

    finally:
        conn.close()


# =========================
# LOGIN
# =========================

@app.route("/system/login", methods=["POST", "OPTIONS"])
def login():
    if flask.request.method == "OPTIONS":
        return "", 200

    data = flask.request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return json.dumps({
            "status": "error",
            "message": "Email e senha são obrigatórios."
        }), 400

    conn = sqlite3.connect("accounts.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM accounts WHERE email = ? AND password = ?",
        (email, password)
    )

    account = cursor.fetchone()
    conn.close()

    if account:
        return json.dumps({
            "status": "success",
            "message": "Login bem-sucedido."
        }), 200
    else:
        return json.dumps({
            "status": "error",
            "message": "Email ou senha incorretos."
        }), 401


# =========================
# RUN
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
