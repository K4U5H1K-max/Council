import { useEffect, useMemo, useRef, useState } from "react";
import ChatMessage from "./ChatMessage";
import TypingIndicator from "./TypingIndicator";

const typingColorMap = {
  blue: "bg-blue-50",
  red: "bg-red-50",
  green: "bg-green-50",
  pink: "bg-pink-50",
  gray: "bg-slate-100",
  yellow: "bg-amber-50",
  purple: "bg-violet-50",
  default: "bg-white",
};

function ChatContainer({ agents, useCase, isLoading, hasPlayed, onPlayed }) {
  const [messages, setMessages] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, currentIndex]);

  useEffect(() => {
    const timers = [];

    if (isLoading || !agents.length) {
      setMessages([]);
      setCurrentIndex(0);
      return () => {
        timers.forEach((timer) => clearTimeout(timer));
      };
    }

    if (hasPlayed) {
      setMessages(agents);
      setCurrentIndex(agents.length);
      return () => {
        timers.forEach((timer) => clearTimeout(timer));
      };
    }

    setMessages([]);
    setCurrentIndex(0);

    const pushMessageSequentially = (index) => {
      if (index >= agents.length) {
        onPlayed?.();
        return;
      }

      setCurrentIndex(index);

      const typingTimer = setTimeout(() => {
        setMessages((previous) => [...previous, agents[index]]);
        setCurrentIndex(index + 1);

        const nextTimer = setTimeout(() => {
          pushMessageSequentially(index + 1);
        }, 320);

        timers.push(nextTimer);
      }, 1250);

      timers.push(typingTimer);
    };

    pushMessageSequentially(0);

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [agents, hasPlayed, isLoading, onPlayed, useCase]);

  const typingAgent = useMemo(() => {
    if (hasPlayed) return null;
    if (isLoading) return null;
    if (currentIndex >= agents.length) return null;
    if (messages.length !== currentIndex) return null;
    return agents[currentIndex];
  }, [agents, currentIndex, hasPlayed, isLoading, messages.length]);

  return (
    <div className="mt-6 max-h-[560px] space-y-4 overflow-y-auto rounded-3xl border border-maroon/20 bg-white/90 p-5 shadow-sm">
      {messages.map((agent, index) => (
        <ChatMessage key={`${agent.id}-${index}`} agent={agent} index={index} />
      ))}

      {typingAgent ? (
        <div className="space-y-1.5">
          <p className={`px-1 text-sm font-semibold uppercase tracking-wide ${currentIndex % 2 === 1 ? "text-right" : "text-left"} text-maroon/75`}>
            {typingAgent.name}
          </p>
          <TypingIndicator
            side={currentIndex % 2 === 0 ? "left" : "right"}
            colorClass={typingColorMap[typingAgent.theme] || typingColorMap.default}
          />
        </div>
      ) : null}

      <div ref={endRef} />
    </div>
  );
}

export default ChatContainer;
