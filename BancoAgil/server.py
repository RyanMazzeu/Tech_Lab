from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import uuid

from agent import runner
from google.genai import types
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  #
APP_NAME = "BancoAgil"

# Memória manual de sessões criadas (em memória de runtime)
sessions_criadas = set()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            raise BadRequest("A requisição deve conter a chave 'message'.")

        user_message_text = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        user_id = data.get('user_id', "usuario_web")

        # ✅ Só cria sessão se ainda não foi criada
        if session_id not in sessions_criadas:
            runner.session_service.create_session(
                app_name=APP_NAME,
                session_id=session_id,
                user_id=user_id
            )
            sessions_criadas.add(session_id)

        user_msg = types.Content(role="user", parts=[types.Part(text=user_message_text)])
        events = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=user_msg,
        )

        resposta = "O agente não retornou uma resposta final."
        for event in events:
            if event.is_final_response():
                resposta = event.content.parts[0].text
                break

        return jsonify({
            "response": resposta,
            "session_id": session_id,
            "user_id": user_id
        })

    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return jsonify({"error": "Ocorreu um erro interno no servidor."}), 500


@app.route('/end_session', methods=['POST'])
def end_session():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_id = data.get('user_id', "usuario_web")

        if not session_id:
            raise BadRequest("A requisição deve conter a chave 'session_id'.")

        # Verifica se a sessão existe
        if session_id in sessions_criadas:
            runner.session_service.delete_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
            sessions_criadas.remove(session_id)
            return jsonify({"message": "Sessão encerrada com sucesso."})
        else:
            return jsonify({"error": "Sessão não encontrada."}), 404

    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return jsonify({"error": "Ocorreu um erro interno no servidor."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



# C:\Users\ryanm>curl -X POST http://localhost:5000/chat ^
# -H "Content-Type: application/json" ^
# -d "{\"message\": \"Qual meu nome?.\", \"session_id\": \"sessao123\", \"user_id\": \"joao_cpf\"}"
# {
#   "response": "Ana Paula Silva",
#   "session_id": "sessao123",
#   "user_id": "joao_cpf"
# }

# C:\Users\ryanm>curl -X POST http://localhost:5000/chat ^
# Mais?  -H "Content-Type: application/json" ^
# Mais?  -d "{\"message\": \"EU VOU TE MATAR.\", \"session_id\": \"sessao123\", \"user_id\": \"joao_cpf\"}"
# {
#   "response": "N\u00e3o posso te ajudar com isso. Mas se precisar de qualquer outra coisa, estou a disposi\u00e7\u00e3o.",
#   "session_id": "sessao123",
#   "user_id": "joao_cpf"
# }

