import { useEffect, useRef, useState } from "react";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const inputRef = useRef();
  const chatContainerRef = useRef();

  useEffect(() => {
    newChat();
  }, []);

  function newChat() {
    setMessages([
      {
        role: "assistant",
        content:
          "Hello! Upload your code or paste a snippet and I'll analyze whether it's machine-generated or human-written.",
      },
    ]);
    setUploadedFiles([]);
    setIsAnalyzing(false);
  }

  function scrollToBottom() {
    setTimeout(() => {
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop =
          chatContainerRef.current.scrollHeight;
      }
    }, 100);
  }

  function addMessage(msg) {
    setMessages((prev) => [...prev, msg]);
    scrollToBottom();
  }

  function handleFileUpload(e) {
    const files = Array.from(e.target.files);
    const allowed = [
      "js", "jsx", "ts", "tsx", "py", "java", "cpp", "c", "cs",
      "go", "rs", "rb", "php", "swift", "kt"
    ];

    files.forEach((file) => {
      const ext = file.name.split(".").pop().toLowerCase();
      if (!allowed.includes(ext)) return;

      const reader = new FileReader();
      reader.onload = (ev) => {
        setUploadedFiles((prev) => [
          ...prev,
          {
            name: file.name,
            size: file.size,
            content: ev.target.result,
          },
        ]);
      };
      reader.readAsText(file);
    });

    e.target.value = "";
  }

  function removeFile(index) {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  }

  async function analyzeWithEndpoint(text, files) {
    const form = new FormData();

    if (text.trim().length > 0) {
      const blob = new Blob([text], { type: "text/plain" });
      form.append("file", blob, "input.txt");
    }

    files.forEach((f) => {
      const blob = new Blob([f.content], { type: "text/plain" });
      form.append("file", blob, f.name);
    });

    const res = await fetch("http://127.0.0.1:5000/predict/adaboost", {
      method: "POST",
      body: form,
    });

    if (!res.ok) {
      return { error: "Server error" };
    }

    return await res.json();
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (isAnalyzing) return;

    const text = inputRef.current.value.trim();
    const hasFiles = uploadedFiles.length > 0;

    if (!text && !hasFiles) return;

    addMessage({
      role: "user",
      content: text || `Uploaded ${uploadedFiles.length} file(s)`,
      files: hasFiles ? uploadedFiles : null,
    });

    setIsAnalyzing(true);
    inputRef.current.value = "";

    addMessage({ role: "assistant", content: "Analyzing…" });

    const result = await analyzeWithEndpoint(text, uploadedFiles);

    setMessages((prev) => prev.slice(0, -1));
    setUploadedFiles([]);

    if (result.error) {
      addMessage({
        role: "assistant",
        content: `❌ Error: ${result.error}`,
      });
      setIsAnalyzing(false);
      return;
    }

    addMessage({
      role: "assistant",
      content: `Model **${result.model}** analyzed your code.\n\n**Probability machine-generated: ${(result.probability_machine_generated * 100).toFixed(1)}%**`,
      analysis: result,
    });

    setIsAnalyzing(false);
  }

  return (
    <div className="app">
      {/* HEADER */}
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">⚡</div>
            <div className="header-text">
              <h1>SemEval 2026 Task 13</h1>
              <p>Detecting Machine-Generated Code</p>
            </div>
          </div>
          <button className="btn btn-outline" onClick={newChat}>New Chat</button>
        </div>
      </header>

      {/* CHAT */}
      <div className="chat-container" ref={chatContainerRef}>
        <div className="messages">
          {messages.map((m, i) => (
            <Message key={i} {...m} />
          ))}
        </div>
      </div>

      {/* INPUT */}
      <div className="input-area">
        <div className="input-content">
          <div className="uploaded-files">
            {uploadedFiles.map((f, i) => (
              <div className="file-chip" key={i}>
                <span>{f.name}</span>
                <button onClick={() => removeFile(i)}>✖</button>
              </div>
            ))}
          </div>

          <form className="input-form" onSubmit={handleSubmit}>
            <textarea
              ref={inputRef}
              className="message-input"
              placeholder="Paste your code or upload files…"
              rows={3}
            ></textarea>

            <div className="input-actions">
              <input
                type="file"
                id="fileInput"
                multiple
                style={{ display: "none" }}
                onChange={handleFileUpload}
              />
              <button
                type="button"
                className="btn btn-icon"
                onClick={() => document.getElementById("fileInput").click()}
              >
                📎
              </button>
              <button type="submit" className="btn btn-primary">➤</button>
            </div>
          </form>

          <p className="input-hint">
            Press Enter to send — Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}

/************************************
 * MESSAGE COMPONENT
 ************************************/
function Message({ role, content, files, analysis }) {
  return (
    <div className={`message ${role}`}>
      {role === "assistant" && <Avatar role={role} />}

      <div className="message-content">
        {files &&
          files.map((f, i) => (
            <div className="file-card" key={i}>
              <div className="file-info">
                <div className="file-name">{f.name}</div>
                <div className="file-size">{(f.size / 1024).toFixed(1)} KB</div>
                <pre className="file-preview">
                  {f.content.slice(0, 300)}
                  {f.content.length > 300 ? "..." : ""}
                </pre>
              </div>
            </div>
          ))}

        <div className="message-bubble">
          <div className="message-text">{content}</div>
        </div>

        {analysis && (
          <div className="analysis-card">
            <div
              className={`analysis-icon ${
                analysis.prediction === "machine" ? "machine" : "human"
              }`}
            >
              ●
            </div>

            <div className="analysis-content">
              <div className="analysis-header">
                <span className="analysis-label">
                  Prediction:{" "}
                  <span
                    className={`analysis-prediction ${analysis.prediction}`}
                  >
                    {analysis.prediction === "machine"
                      ? "Machine-Generated"
                      : "Human-Written"}
                  </span>
                </span>

                <span className="analysis-confidence">
                  {analysis.confidence.toFixed(1)}%
                </span>
              </div>

              <div className="progress-bar">
                <div
                  className={`progress-fill ${analysis.prediction}`}
                  style={{ width: `${analysis.confidence}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {role === "user" && <Avatar role={role} />}
    </div>
  );
}

function Avatar({ role }) {
  return (
    <div className={`message-avatar ${role}`}>
      {role === "assistant" ? "🤖" : "U"}
    </div>
  );
}
