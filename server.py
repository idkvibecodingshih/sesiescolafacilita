import flask
import flask_cors
import json
from openai import OpenAI
import os


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
        "content": """
"""
    }
]
        


    def call(self, pergunta: str):

        # adiciona pergunta
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
        self.adicionar_memoria_personalidade(pergunta, resposta)

        # adiciona resposta
        self.memoria.append({
            "role": "assistant",
            "content": resposta
        })

        return self.format(resposta)



IA_instance = IA(
    base_url="https://api.groq.com/openai/v1",
    api_key=ENV_API_KEY
)


app = flask.Flask(__name__)
flask_cors.CORS(app)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = flask.request.get_json()
    print("Received question:", data)

    resposta = IA_instance.call(data["question"])

    response = {
        "status": "success",
        "message": f"{resposta}"
    }
    return json.dumps(response), 200


if __name__ == "__main__":
    app.run(debug=True)
