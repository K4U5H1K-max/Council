import { motion } from "framer-motion";

function DecisionPanel({ finalDecision }) {
  const winner = finalDecision?.winner || "Draw";
  const summary = finalDecision?.summary || "";
  const proAnalysis = finalDecision?.pro_analysis || "";
  const conAnalysis = finalDecision?.con_analysis || "";
  const criticalFactors = finalDecision?.critical_factors || "";
  const reasoning = finalDecision?.reasoning || "";

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32 }}
      className="space-y-6"
    >
      {/* Winner Badge */}
      <div className="rounded-3xl border border-maroon/35 bg-gradient-to-r from-rose-50 to-amber-50 p-8 shadow-panel ring-1 ring-maroon/25">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-maroon sm:text-4xl">Final Decision</h2>
            <p className="mt-2 inline-flex rounded-full border border-maroon/25 bg-white/80 px-4 py-2 text-sm font-semibold uppercase tracking-wide text-maroon">
              Winner: {winner}
            </p>
          </div>
          <div className={`text-6xl font-bold ${winner === "Pro" ? "text-green-600" : winner === "Con" ? "text-red-600" : "text-slate-400"}`}>
            {winner === "Pro" ? "✓" : winner === "Con" ? "✗" : "⚖"}
          </div>
        </div>
      </div>

      {/* Summary Section */}
      {summary && (
        <div className="rounded-2xl border border-maroon/25 bg-white/85 p-6">
          <h3 className="text-xl font-semibold uppercase tracking-wide text-maroon">Debate Summary</h3>
          <p className="mt-3 text-lg leading-relaxed text-maroon/85">{summary}</p>
        </div>
      )}

      {/* Pro & Con Analysis */}
      <div className="grid gap-6 sm:grid-cols-2">
        {proAnalysis && (
          <div className="rounded-2xl border border-green-200 bg-green-50/50 p-6">
            <h3 className="text-lg font-semibold text-green-900">Pro Analysis</h3>
            <p className="mt-3 text-sm leading-relaxed text-green-900/80">{proAnalysis}</p>
          </div>
        )}
        {conAnalysis && (
          <div className="rounded-2xl border border-red-200 bg-red-50/50 p-6">
            <h3 className="text-lg font-semibold text-red-900">Con Analysis</h3>
            <p className="mt-3 text-sm leading-relaxed text-red-900/80">{conAnalysis}</p>
          </div>
        )}
      </div>

      {/* Critical Factors */}
      {criticalFactors && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50/50 p-6">
          <h3 className="text-lg font-semibold text-amber-900">Critical Turning Points</h3>
          <p className="mt-3 text-sm leading-relaxed text-amber-900/80">{criticalFactors}</p>
        </div>
      )}

      {/* Reasoning */}
      {reasoning && (
        <div className="rounded-2xl border border-maroon/25 bg-white/85 p-6">
          <h3 className="text-lg font-semibold uppercase tracking-wide text-maroon">Final Reasoning</h3>
          <p className="mt-3 text-base leading-relaxed text-maroon/85">{reasoning}</p>
        </div>
      )}

      {/* Key Insights */}
      {finalDecision?.insights && finalDecision.insights.length > 0 && (
        <div className="rounded-2xl border border-maroon/25 bg-white/85 p-6">
          <h3 className="text-lg font-semibold uppercase tracking-wide text-maroon">Key Takeaways</h3>
          <ul className="mt-4 list-disc space-y-2 pl-6 text-sm text-maroon/85">
            {finalDecision.insights.map((insight, idx) => (
              <li key={idx}>{insight}</li>
            ))}
          </ul>
        </div>
      )}
    </motion.section>
  );
}

export default DecisionPanel;
