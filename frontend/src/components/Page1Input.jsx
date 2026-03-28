import { motion } from "framer-motion";
import { useCaseOptions } from "../config/agentConfigs";

function Page1Input({
  userInput,
  useCase,
  onInputChange,
  onUseCaseChange,
  personalContext,
  personalContextTags,
  onPersonalContextChange,
  onPersonalContextSave,
  onNext,
  isLoading,
}) {
  const modeLabel = useCase === "personal" ? "Personal" : "What-if";

  return (
    <section className="w-full shrink-0 p-4 sm:p-6 lg:p-8 animate-floatIn">
      <div className="mx-auto max-w-4xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <h2 className="text-2xl font-semibold text-slate-900">Enter Your Dilemma</h2>
        <p className="mt-2 text-sm text-slate-600">
          Describe the decision context so the council can simulate competing viewpoints.
        </p>

        <motion.p
          key={modeLabel}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mt-4 inline-flex rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700"
        >
          Mode: {modeLabel}
        </motion.p>

        <div className="mt-5 space-y-5">
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

          <div className="rounded-2xl border border-cyan-200 bg-cyan-50/60 p-4 sm:p-5">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-cyan-800">Personal Context</h3>
            <p className="mt-1 text-xs text-cyan-900/80">
              Add context signals so the council can personalize its recommendations.
            </p>

            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label htmlFor="context-q1" className="text-xs font-medium text-slate-700">
                  Q1. What outcome matters most right now?
                </label>
                <input
                  id="context-q1"
                  type="text"
                  value={personalContext.q1}
                  onChange={(event) => onPersonalContextChange("q1", event.target.value)}
                  placeholder="Example: Stability with steady growth"
                  className="w-full rounded-xl border border-cyan-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-cyan-400 transition focus:ring"
                />
              </div>

              <div className="space-y-1.5">
                <label htmlFor="context-q2" className="text-xs font-medium text-slate-700">
                  Q2. What constraint should we avoid violating?
                </label>
                <input
                  id="context-q2"
                  type="text"
                  value={personalContext.q2}
                  onChange={(event) => onPersonalContextChange("q2", event.target.value)}
                  placeholder="Example: Burnout or budget overrun"
                  className="w-full rounded-xl border border-cyan-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-cyan-400 transition focus:ring"
                />
              </div>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-3">
              <motion.button
                type="button"
                whileTap={{ scale: 0.97 }}
                onClick={onPersonalContextSave}
                className="rounded-xl border border-cyan-600 bg-white px-4 py-2 text-xs font-semibold text-cyan-700 transition hover:bg-cyan-100"
              >
                Save Context
              </motion.button>

              {personalContextTags.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {personalContextTags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full border border-cyan-300 bg-white px-2.5 py-1 text-xs font-medium text-cyan-800"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          </div>

          <div className="pt-2">
            <motion.button
              type="button"
              whileTap={{ scale: 0.98 }}
              onClick={onNext}
              disabled={!userInput.trim() || isLoading}
              className="rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-500 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? "Preparing..." : "Next"}
            </motion.button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Page1Input;
