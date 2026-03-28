function DecisionPanel({ finalDecision }) {
  return (
    <section className="rounded-2xl border border-teal-200 bg-gradient-to-r from-teal-50 to-cyan-50 p-5 shadow-panel animate-floatIn">
      <h2 className="text-lg font-semibold text-slate-900">Final Decision Panel</h2>

      <p className="mt-3 text-sm leading-relaxed text-slate-700">
        {finalDecision.text}
      </p>

      <div className="mt-4 flex flex-wrap gap-3 text-xs sm:text-sm">
        <span className="rounded-full bg-white px-3 py-1 font-medium text-slate-700">
          Influencing Agent: {finalDecision.influencingAgent}
        </span>
        <span className="rounded-full bg-white px-3 py-1 font-medium text-slate-700">
          Confidence: {Math.round(finalDecision.confidence * 100)}%
        </span>
      </div>
    </section>
  );
}

export default DecisionPanel;
