function InputPanel({
  userInput,
  decisionType,
  onInputChange,
  onTypeChange,
  onSubmit,
  isLoading,
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-panel backdrop-blur animate-floatIn">
      <h2 className="text-lg font-semibold text-slate-900">Input Panel</h2>
      <p className="mt-1 text-sm text-slate-600">
        Enter a dilemma and choose simulation mode.
      </p>

      <form className="mt-4 space-y-4" onSubmit={onSubmit}>
        <textarea
          value={userInput}
          onChange={(event) => onInputChange(event.target.value)}
          rows={4}
          placeholder="Example: Should we prioritize long-term growth over short-term stability for the team?"
          className="w-full rounded-xl border border-slate-300 bg-white p-3 text-sm text-slate-900 outline-none ring-teal-500 transition focus:ring"
        />

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <select
            value={decisionType}
            onChange={(event) => onTypeChange(event.target.value)}
            className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-teal-500 transition focus:ring"
          >
            <option>Personal Decision</option>
            <option>Scenario Simulation</option>
          </select>

          <button
            type="submit"
            disabled={isLoading}
            className="rounded-xl border border-teal-600 px-4 py-2 text-sm font-semibold text-teal-700 transition hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Submit Dilemma
          </button>
        </div>
      </form>
    </section>
  );
}

export default InputPanel;
