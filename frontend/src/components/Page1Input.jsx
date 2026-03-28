import { useCaseOptions } from "../config/agentConfigs";

function Page1Input({
  userInput,
  useCase,
  onInputChange,
  onUseCaseChange,
  onNext,
  isLoading,
}) {
  return (
    <section className="w-full shrink-0 p-4 sm:p-6 lg:p-8 animate-floatIn">
      <div className="mx-auto max-w-3xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-semibold text-slate-900">Enter Your Dilemma</h2>
        <p className="mt-2 text-sm text-slate-600">
          Describe the decision context so the council can simulate competing viewpoints.
        </p>

        <div className="mt-5 space-y-4">
          <textarea
            value={userInput}
            onChange={(event) => onInputChange(event.target.value)}
            rows={6}
            placeholder="Example: Should we expand into a new market now or focus on strengthening current operations first?"
            className="w-full rounded-xl border border-slate-300 bg-white p-3 text-sm text-slate-900 outline-none ring-teal-500 transition focus:ring"
          />

          <div className="space-y-2">
            <label htmlFor="use-case" className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Select Use-Case
            </label>
            <select
              id="use-case"
              value={useCase}
              onChange={(event) => onUseCaseChange(event.target.value)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-teal-500 transition focus:ring"
            >
              {useCaseOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="pt-2">
            <button
              type="button"
              onClick={onNext}
              disabled={!userInput.trim() || isLoading}
              className="rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? "Preparing..." : "Next"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Page1Input;
