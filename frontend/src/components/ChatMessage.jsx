import { motion } from "framer-motion";

const bubbleColorMap = {
  blue: "bg-blue-50 border-blue-200 text-blue-900",
  red: "bg-red-50 border-red-200 text-red-900",
  green: "bg-green-50 border-green-200 text-green-900",
  pink: "bg-pink-50 border-pink-200 text-pink-900",
  gray: "bg-slate-100 border-slate-200 text-slate-900",
  yellow: "bg-amber-50 border-amber-200 text-amber-900",
  purple: "bg-violet-50 border-violet-200 text-violet-900",
  default: "bg-white border-maroon/20 text-maroon",
};

function ChatMessage({ agent, index }) {
  const side = index % 2 === 0 ? "left" : "right";
  const alignment = side === "right" ? "justify-end" : "justify-start";
  const enterX = side === "right" ? 20 : -20;
  const bubbleColors = bubbleColorMap[agent.theme] || bubbleColorMap.default;

  return (
    <motion.div
      initial={{ opacity: 0, x: enterX, y: 6 }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{ duration: 0.32, ease: "easeOut" }}
      className={`flex ${alignment} px-1`}
    >
      <div className={`max-w-[84%] rounded-3xl border px-4 py-3.5 shadow-sm ${bubbleColors}`}>
        <p className="text-sm font-semibold uppercase tracking-wide text-maroon/75">
          {agent.name}
        </p>
        <p className="mt-2 text-lg leading-relaxed">{agent.proposal}</p>
      </div>
    </motion.div>
  );
}

export default ChatMessage;
