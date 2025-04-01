
import { format } from "date-fns";

interface Message {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.sender === "user";
  const time = format(new Date(message.timestamp), "h:mm a");

  return (
    <div
      className={`flex items-start gap-3 animate-fade-in ${
        isUser ? "flex-row-reverse" : ""
      }`}
    >
      <div
        className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-blue-100 text-blue-600"
        }`}
      >
        <span className="text-sm font-semibold">
          {isUser ? "You" : "AI"}
        </span>
      </div>
      
      <div
        className={`px-4 py-3 rounded-2xl max-w-[80%] relative group ${
          isUser
            ? "bg-blue-600 text-white rounded-tr-none"
            : "bg-gray-100 text-gray-800 rounded-tl-none"
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
        <div
          className={`text-[10px] mt-1 opacity-0 group-hover:opacity-100 transition-opacity ${
            isUser ? "text-blue-200 text-right" : "text-gray-500"
          }`}
        >
          {time}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
