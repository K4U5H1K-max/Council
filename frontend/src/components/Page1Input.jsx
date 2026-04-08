import { motion } from "framer-motion";
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
      <div className="mx-auto max-w-4xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <h2 className="text-2xl font-semibold text-slate-900">Start a New Debate</h2>
        <p className="mt-2 text-sm text-slate-600">
          Enter a topic or question to initiate a structured 3-round debate between Pro and Con agents.
        </p>

        <div className="mt-5 space-y-5">
          <textarea
            value={userInput}
            onChange={(event) => onInputChange(event.target.value)}
            rows={6}
            placeholder="Example: Is artificial intelligence a net positive for society? Should we expand into a new market now or focus on strengthening current operations first?"
            className="w-full rounded-xl border border-slate-300 bg-white p-3 text-sm text-slate-900 outline-none ring-teal-500 transition focus:ring"
          />

          <div className="pt-2">
            <motion.button
              type="button"
              whileTap={{ scale: 0.98 }}
              onClick={onNext}
              disabled={!userInput.trim() || isLoading}
              className="rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-500 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? "Preparing..." : "Start Debate"}
            </motion.button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Page1Input;
