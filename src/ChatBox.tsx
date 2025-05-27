import { useState, useRef, useEffect } from 'react';

export default function ChatBox() {
  const [messages, setMessages] = useState<{ role: 'user' | 'bot'; text: string }[]>([]);
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage = { role: 'user', text: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    // Optionally auto-resize textarea height back down
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    // Simulate bot response
    const botMessage = { role: 'bot', text: `Echo: ${trimmed}` };
    setTimeout(() => {
      setMessages((prev) => [...prev, botMessage]);
    }, 500);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    // Auto-grow the textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  return (
    <div className="flex flex-col max-w-2xl mx-auto h-[80vh] bg-white rounded-xl border shadow overflow-hidden">
      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`text-sm whitespace-pre-wrap ${
              msg.role === 'user' ? 'text-right text-gray-900' : 'text-left text-blue-600'
            }`}
          >
            <span className="block px-3 py-2 bg-gray-100 rounded inline-block max-w-[80%]">
              {msg.text}
            </span>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="border-t p-3">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            rows={1}
            className="w-full resize-none text-sm border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring focus:ring-indigo-300"
          />
          <button
            type="button"
            onClick={handleSend}
            className="absolute right-2 bottom-2 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
