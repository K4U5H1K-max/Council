function DebatePanel({ messages }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-panel backdrop-blur animate-floatIn">
      <h2 className="text-lg font-semibold text-slate-900">Critique / Debate Panel</h2>
      <p className="mt-1 text-sm text-slate-600">
        Agents challenge and refine each other&apos;s proposals.
      </p>

      <div className="mt-4 max-h-72 space-y-3 overflow-y-auto pr-1">
        {messages.map((message) => (
          <div
            key={message.id}
            className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm leading-relaxed"
          >
            <span className="font-semibold text-slate-900">[{message.agent}]</span>{" "}
            <span className="text-slate-700">{message.text}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default DebatePanel;
