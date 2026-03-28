import AgentGrid from "./AgentGrid";
import DebatePanel from "./DebatePanel";

function Page2Agents({ agents, critiqueMessages, useCaseLabel, useCase, onNext, isLoading }) {
  return (
    <section className="w-full shrink-0 p-4 sm:p-6 lg:p-8 animate-floatIn">
      <div className="space-y-5">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-2xl font-semibold text-slate-900">Agent Interaction</h2>
          <p className="mt-1 text-sm text-slate-600">
            Proposals and critiques evolve through collaborative disagreement.
          </p>
          <p className="mt-3 inline-flex rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700">
            Mode: {useCaseLabel}
          </p>
        </div>

        <AgentGrid agents={agents} useCase={useCase} />
        <DebatePanel messages={critiqueMessages} />

        <div className="flex justify-end">
          <button
            type="button"
            onClick={onNext}
            disabled={isLoading}
            className="rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Next
          </button>
        </div>
      </div>
    </section>
  );
}

export default Page2Agents;
