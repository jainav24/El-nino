import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Mic, Send, Plus, X, BrainCircuit, Activity, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ChatMessage {
  role: 'user' | 'model';
  content: string;
}

export default function FloatingAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false); // When typing, expands the bar
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [thinkMode, setThinkMode] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const location = useLocation();

  // Speech Recognition (Web Speech API)
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const hasSpeechSupport = !!SpeechRecognition;

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = async (text: string = inputValue) => {
    if (!text.trim() || isLoading) return;

    const newMessages = [...messages, { role: 'user', content: text } as ChatMessage];
    setMessages(newMessages);
    setInputValue('');
    setIsOpen(true);
    setIsExpanded(true);
    setIsLoading(true);

    try {
      let riskContext = null;
      if (location.pathname.includes('risk')) {
        try {
          const stored = localStorage.getItem('latest_risk_prediction');
          if (stored) riskContext = JSON.parse(stored);
        } catch(e) {}
      }

      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: newMessages,
          page_context: {
            pathname: location.pathname,
            search: location.search
          },
          risk_context: riskContext,
          think_mode: thinkMode
        })
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      setMessages([...newMessages, { role: 'model', content: data.response }]);
    } catch (error) {
      console.error(error);
      setMessages([...newMessages, { role: 'model', content: 'Sorry, I encountered an error connecting to the AI.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleMic = () => {
    if (!hasSpeechSupport) return;
    
    if (isListening) {
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInputValue((prev) => prev + (prev ? ' ' : '') + transcript);
      setIsExpanded(true);
    };

    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    
    recognition.start();
  };

  const handleMenuAction = (action: string) => {
    setShowMenu(false);
    if (action === 'clear') {
      setMessages([]);
      setIsOpen(false);
      setIsExpanded(false);
    } else {
      handleSend(action);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end pointer-events-none">
      
      {/* Chat Window */}
      <div 
        className={`bg-white border border-slate-200 rounded-2xl shadow-2xl mb-4 flex flex-col overflow-hidden transition-all duration-200 transform origin-bottom-right ${
          isOpen ? 'opacity-100 scale-100 translate-y-0 pointer-events-auto' : 'opacity-0 scale-95 translate-y-4 pointer-events-none'
        }`}
        style={{
          width: 'calc(100vw - 48px)',
          maxWidth: '400px',
          height: '70vh',
          maxHeight: '600px'
        }}
      >
        {/* Chat Header */}
        <div className="px-5 py-4 border-b border-slate-100 flex justify-between items-center bg-white">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-slate-800 text-sm">AgriRisk AI</h3>
              <p className="text-xs text-slate-500">AI Insurance Assistant</p>
            </div>
          </div>
          <button 
            onClick={() => setIsOpen(false)} 
            className="text-slate-400 hover:text-slate-600 hover:bg-slate-100 p-2 rounded-full transition-colors"
            aria-label="Close AgriRisk AI Assistant"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Chat Body */}
        <div className="flex-1 p-4 overflow-y-auto flex flex-col space-y-4 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent bg-slate-50">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 py-8 px-4">
              <Bot className="w-12 h-12 text-slate-300 mb-3" />
              <p className="text-sm font-medium text-slate-600 mb-1">How can I help you today?</p>
              <p className="text-xs text-slate-400">Ask about risk analysis, policies, or weather data.</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm shadow-sm ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-sm' 
                    : 'bg-white text-slate-700 border border-slate-200 rounded-bl-sm prose prose-sm max-w-none'
                }`}>
                  {msg.role === 'user' ? msg.content : <ReactMarkdown>{msg.content}</ReactMarkdown>}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3 flex space-x-1.5 items-center shadow-sm">
                <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Chat Input Container */}
        <div className="p-3 border-t border-slate-100 bg-white">
          <div className="flex items-center space-x-2">
            
            {/* Main Pill */}
            <div className="flex-1 relative bg-slate-50 border border-slate-200 rounded-full flex items-center shadow-sm focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all">
              
              {/* Plus Menu Button */}
              <div className="relative">
                <button 
                  onClick={() => setShowMenu(!showMenu)}
                  className="p-2.5 pl-3 text-slate-400 hover:text-blue-600 transition-colors flex items-center justify-center rounded-l-full"
                >
                  <Plus className={`w-5 h-5 transition-transform duration-200 ${showMenu ? 'rotate-45' : ''}`} />
                </button>
                
                {showMenu && (
                  <div className="absolute bottom-full left-0 mb-2 w-48 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden py-1 z-10 text-sm">
                    <button onClick={() => handleMenuAction('Explain this page')} className="w-full text-left px-4 py-2 text-slate-600 hover:bg-slate-50 hover:text-blue-600 transition-colors">Explain this page</button>
                    <button onClick={() => handleMenuAction('Explain the current chart')} className="w-full text-left px-4 py-2 text-slate-600 hover:bg-slate-50 hover:text-blue-600 transition-colors">Explain this chart</button>
                    <button onClick={() => handleMenuAction('What is Survival Analysis?')} className="w-full text-left px-4 py-2 text-slate-600 hover:bg-slate-50 hover:text-blue-600 transition-colors">What is Survival Analysis?</button>
                    <div className="h-px bg-slate-100 my-1" />
                    <button onClick={() => handleMenuAction('clear')} className="w-full text-left px-4 py-2 text-rose-500 hover:bg-slate-50 transition-colors">Clear conversation</button>
                  </div>
                )}
              </div>

              {/* Text Input */}
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything..."
                className="flex-1 bg-transparent border-none outline-none text-slate-700 text-sm placeholder-slate-400 py-2.5 px-1"
              />

              {/* Action Buttons */}
              <div className="flex items-center pr-2 space-x-1">
                <button 
                  onClick={() => setThinkMode(!thinkMode)}
                  title="Think Mode (Detailed Answers)"
                  className={`p-1.5 rounded-full transition-colors ${thinkMode ? 'text-amber-500 bg-amber-50' : 'text-slate-400 hover:text-slate-600'}`}
                >
                  <BrainCircuit className="w-4 h-4" />
                </button>

                {hasSpeechSupport && (
                  <button 
                    onClick={toggleMic}
                    title="Voice Input"
                    className={`p-1.5 rounded-full transition-colors ${isListening ? 'text-rose-500 bg-rose-50 animate-pulse' : 'text-slate-400 hover:text-slate-600'}`}
                  >
                    <Mic className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Send Button */}
            <button 
              onClick={() => handleSend()}
              disabled={!inputValue.trim() || isLoading}
              className={`flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full transition-all ${
                inputValue.trim() && !isLoading 
                  ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md scale-105' 
                  : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              }`}
            >
              {isLoading ? <Activity className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 ml-0.5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Floating Robot Launcher Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? "Close AgriRisk AI Assistant" : "Open AgriRisk AI Assistant"}
        className={`w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 z-50 pointer-events-auto ${
          isOpen ? 'opacity-0 scale-0 absolute' : 'opacity-100 scale-100 bg-blue-600 hover:bg-blue-700 text-white hover:shadow-xl'
        }`}
      >
        <Bot className="w-7 h-7" />
      </button>

    </div>
  );
}
