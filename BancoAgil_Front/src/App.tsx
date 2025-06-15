import { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

// Define a interface para as mensagens do chat
interface ChatMessage {
  from: "user" | "bot" | "system"; // Adicionado "system" para mensagens do sistema
  text: string;
}

function App() {
  // --- ESTILOS CSS ---
  // O CSS foi movido para dentro do componente para evitar erros de importação.


  // --- STATE HOOKS ---
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const [sessionId] = useState(`sessao_${Date.now()}`);
  const [userId] = useState("joao_cpf");
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // --- EFFECTS ---
  // Rola para a mensagem mais recente sempre que o chat for atualizado
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  // --- FUNÇÕES ---
  const sendMessage = async () => {
    if (!message.trim() || isLoading) return;
    setChat((prev) => [...prev, { from: "user", text: message }]);
    setIsLoading(true);
    setChat((prev) => [...prev, { from: "bot", text: "..." }]);

    try {
      const response = await axios.post("http://localhost:5000/chat", {
        message,
        session_id: sessionId,
        user_id: userId,
      });
      setChat((prev) => [
        ...prev.slice(0, -1),
        { from: "bot", text: response.data.response },
      ]);
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
      setChat((prev) => [
        ...prev.slice(0, -1),
        {
          from: "bot",
          text: "Não foi possível conectar ao servidor. Tente novamente.",
        },
      ]);
    }
    setMessage("");
    setIsLoading(false);
  };

  const endChatSession = async () => {
    if (isLoading) return;
    setIsLoading(true);
    try {
      await axios.post("http://localhost:5000/end_session", {
        session_id: sessionId,
        user_id: userId,
      });
      setChat((prev) => [
        ...prev,
        { from: "system", text: "Sessão encerrada com sucesso." },
      ]);
    } catch (error) {
      console.error("Erro ao encerrar a sessão:", error);
      setChat((prev) => [
        ...prev,
        { from: "system", text: "Erro ao tentar encerrar a sessão." },
      ]);
    }
    setMessage("");
    // Mantém o input desabilitado para indicar que a sessão acabou
  };

  // --- RENDER ---
  return (
    <>
      <div className="app">
        <h1>Banco Ágil 🏦</h1>
        <div className="chat-box">
          {chat.map((entry, index) => (
            <div key={index} className={`chat-message ${entry.from}`}>
              {entry.text === "..." ? (
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              ) : (
                <span>{entry.text}</span>
              )}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <div className="input-area">
          <input
            type="text"
            placeholder="Digite sua pergunta..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            disabled={isLoading}
          />
          <button onClick={sendMessage} disabled={isLoading}>
            {isLoading ? "Aguarde..." : "Enviar"}
          </button>
          <button
            onClick={endChatSession}
            disabled={isLoading}
            className="end-chat-button"
          >
            Encerrar Chat
          </button>
        </div>
      </div>
    </>
  );
}

export default App;
