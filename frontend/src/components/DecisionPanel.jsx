import { motion } from "framer-motion";

function DecisionPanel({ finalDecision }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32 }}
      className="rounded-3xl border border-maroon/35 bg-gradient-to-r from-rose-50 to-amber-50 p-8 shadow-panel ring-1 ring-maroon/25"
    >
      <h2 className="text-3xl font-bold text-maroon sm:text-4xl">Council Decision</h2>

      <p className="mt-5 whitespace-pre-line text-lg leading-relaxed text-maroon/85">
        {finalDecision.text}
      </p>

      <div className="mt-7 rounded-2xl border border-maroon/25 bg-white/85 p-6">
        <h3 className="text-xl font-semibold uppercase tracking-wide text-maroon">Key Insights</h3>
        <ul className="mt-4 list-disc space-y-2 pl-6 text-lg text-maroon/85">
          {(finalDecision.insights || []).map((insight) => (
            <li key={insight}>{insight}</li>
          ))}
        </ul>
      </div>
    </motion.section>
  );
}

export default DecisionPanel;
