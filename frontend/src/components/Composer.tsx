import { Mic, SendHorizontal, Sparkles } from "lucide-react";
import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";

interface ComposerProps {
  disabled: boolean;
  onSend: (message: string) => void;
}

export function Composer({ disabled, onSend }: ComposerProps) {
  const [value, setValue] = useState("");
  const [listening, setListening] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const handleGlobalKeyDown = (e: globalThis.KeyboardEvent) => {
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }
      if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleGlobalKeyDown);
    return () => window.removeEventListener("keydown", handleGlobalKeyDown);
  }, []);

  const startVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support voice input.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.onstart = () => setListening(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setValue((prev) => prev + (prev ? " " : "") + transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognition.start();
  };

  const submit = () => {
    const message = value.trim();
    if (!message || disabled) return;
    setValue("");
    onSend(message);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    submit();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <div className="composer__field">
        <button
          type="button"
          onClick={startVoice}
          className="voice-btn"
          title="Use voice input"
          aria-label="Use voice input"
          style={{
            background: listening ? "var(--danger)" : "var(--brand-soft)",
            color: listening ? "white" : "var(--brand)",
            border: "none",
            borderRadius: "50%",
            width: "32px",
            height: "32px",
            display: "grid",
            placeItems: "center",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            cursor: "pointer",
            flexShrink: 0,
            transition: "all 0.2s ease",
            transform: listening ? "scale(1.1)" : "scale(1)",
            animation: listening ? "pulse 1.5s infinite" : "none"
          }}
        >
          {listening ? <span style={{ width: 8, height: 8, background: 'white', borderRadius: '50%' }} /> : <Mic size={16} />}
        </button>
        <textarea
          ref={inputRef}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Tell me what you're shopping for…"
          rows={1}
          disabled={disabled}
          autoFocus
          aria-label="Message the shopping assistant"
        />
        <button
          type="submit"
          className="send-btn"
          disabled={disabled || !value.trim()}
          aria-label="Send message"
        >
          <SendHorizontal size={19} />
        </button>
      </div>
      <p>Enter to send · Shift + Enter for a new line</p>
    </form>
  );
}
