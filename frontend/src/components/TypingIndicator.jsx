import { motion } from "framer-motion";

function TypingIndicator({ side = "left", colorClass = "bg-slate-100" }) {
  const alignment = side === "right" ? "justify-end" : "justify-start";

  return (
    <div className={`flex ${alignment} px-1`}>
      <div className={`max-w-[80%] rounded-2xl px-3 py-2 shadow-sm ${colorClass}`}>
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map((dot) => (
            <motion.span
              key={dot}
              className="h-1.5 w-1.5 rounded-full bg-maroon/70"
              animate={{ opacity: [0.35, 1, 0.35], y: [0, -1, 0] }}
              transition={{
                duration: 0.9,
                repeat: Infinity,
                delay: dot * 0.16,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default TypingIndicator;
