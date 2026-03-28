import { motion } from "framer-motion";

function DebatePanel({ messages, isLoading }) {
  const compactMessages = messages.slice(0, 3);

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-panel backdrop-blur"
    >
      <h2 className="text-lg font-semibold text-slate-900">Consensus</h2>
      <p className="mt-1 text-sm text-slate-600">
        Quick view of where the council broadly aligns.
      </p>

      {isLoading ? (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500">
          Generating consensus highlights...
        </div>
      ) : (
        <div className="mt-4 max-h-72 space-y-3 overflow-y-auto pr-1">
          {compactMessages.map((message) => (
            <div
              key={message.id}
              className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm leading-relaxed"
            >
              <span className="font-semibold text-slate-900">[{message.agent}]</span>{" "}
              <span className="text-slate-700">{message.text}</span>
            </div>
          ))}
        </div>
      )}
    </motion.section>
  );
}

export default DebatePanel;
