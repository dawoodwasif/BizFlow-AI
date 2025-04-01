
import { RefreshCw, Menu, Home } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ChatHeaderProps {
  clearChat: () => void;
}

const ChatHeader = ({ clearChat }: ChatHeaderProps) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm py-4">
      <div className="container mx-auto px-4 max-w-4xl flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
            <span className="text-white font-bold text-lg">B</span>
          </div>
          <h1 className="text-xl font-bold text-gray-800">BizFlow AI</h1>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => navigate("/home")}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
            title="Home"
          >
            <Home className="h-5 w-5" />
          </button>
          
          <button
            onClick={clearChat}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
            title="Clear chat"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                title="Settings"
              >
                <Menu className="h-5 w-5" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={clearChat}>
                Reset Conversation
              </DropdownMenuItem>
              <DropdownMenuItem>
                API Settings
              </DropdownMenuItem>
              <DropdownMenuItem>
                Help Center
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};

export default ChatHeader;
