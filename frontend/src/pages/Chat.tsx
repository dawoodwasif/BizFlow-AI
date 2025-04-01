
import { useState, useRef, useEffect } from "react";
import { SendIcon, RefreshCw, ChevronDown } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import ChatMessage from "@/components/ChatMessage";
import ChatHeader from "@/components/ChatHeader";
import LoadingDots from "@/components/LoadingDots";

interface Message {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: Date;
}

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // API endpoint for the Rasa server
  const API_URL = "http://localhost:5005/webhooks/rest/webhook";

  // Add a welcome message when the component mounts
  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        content: "Hi there! I'm BizFlow AI. How can I help you today?",
        sender: "assistant",
        timestamp: new Date(),
      },
    ]);
  }, []);

  // Auto-scroll to the bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const generateId = () => {
    return Math.random().toString(36).substring(2, 11);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message
    const userMessage: Message = {
      id: generateId(),
      content: input,
      sender: "user",
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input.trim(),
          sender: "enterprise_user",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data && data.length > 0 && data[0].text) {
        const botResponse: Message = {
          id: generateId(),
          content: data[0].text,
          sender: "assistant",
          timestamp: new Date(),
        };
        
        setMessages((prev) => [...prev, botResponse]);
      } else {
        throw new Error("No valid response received");
      }
    } catch (err) {
      console.error("Error:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to connect to the server. Please try again."
      );
      
      toast({
        title: "Error",
        description: "Could not connect to BizFlow AI. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome",
        content: "Hi there! I'm BizFlow AI. How can I help you today?",
        sender: "assistant",
        timestamp: new Date(),
      },
    ]);
    toast({
      title: "Chat cleared",
      description: "Your conversation has been reset.",
    });
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 to-gray-50">
      <ChatHeader clearChat={clearChat} />
      
      <main className="flex-grow container mx-auto px-4 py-6 max-w-4xl">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-100 flex flex-col h-[80vh]">
          {/* Chat messages area */}
          <div 
            ref={chatContainerRef}
            className="flex-grow overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-blue-50/30 to-transparent"
          >
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            
            {isLoading && (
              <div className="flex items-start gap-3 animate-fade-in">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <span className="text-blue-600 text-sm font-semibold">AI</span>
                </div>
                <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%]">
                  <LoadingDots />
                </div>
              </div>
            )}
            
            {error && (
              <div className="flex items-start gap-3 animate-fade-in">
                <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                  <span className="text-red-600 text-sm font-semibold">!</span>
                </div>
                <div className="bg-red-50 text-red-600 rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%]">
                  {error}
                  <button
                    onClick={() => setError(null)}
                    className="text-xs underline ml-2"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input area */}
          <div className="p-4 border-t border-gray-200 bg-white">
            <form onSubmit={handleSubmit} className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
                placeholder="Type your message here..."
                className="flex-grow px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className={`p-3 rounded-full text-white transition-colors ${
                  isLoading || !input.trim()
                    ? "bg-gray-300"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                <SendIcon className="h-5 w-5" />
              </button>
            </form>
            <div className="text-xs text-center mt-2 text-gray-400">
              BizFlow AI • Streamlining your business processes
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
