import { SendHorizontal, Sparkles } from "lucide-react";
import { FormEvent, KeyboardEvent, useState } from "react";

interface ComposerProps {
  disabled: boolean;
  onSend: (message: string) => void;
}

export function Composer({ disabled, onSend }: ComposerProps) {
  const [value, setValue] = useState("");

  const submit = () => {
    const message = value.trim();
    if (!message || disabled) return;
    setValue("");
    onSend(message);
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
        <Sparkles size={17} aria-hidden="true" />
        <textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Tell me what you're shopping for…"
          rows={1}
          disabled={disabled}
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
