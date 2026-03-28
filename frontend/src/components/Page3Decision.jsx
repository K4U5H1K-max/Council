import DecisionPanel from "./DecisionPanel";
import TrustPanel from "./TrustPanel";

function Page3Decision({ finalDecision, trustMatrix, onRestart }) {
  return (
    <section className="w-full shrink-0 p-4 sm:p-6 lg:p-8 animate-floatIn">
      <div className="space-y-5">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-2xl font-semibold text-slate-900">Final Output</h2>
          <p className="mt-1 text-sm text-slate-600">
            Consolidated decision and relationship memory after simulation.
          </p>
        </div>

        <DecisionPanel finalDecision={finalDecision} />
        <TrustPanel trustMatrix={trustMatrix} />

        <div className="flex justify-end">
          <button
            type="button"
            onClick={onRestart}
            className="rounded-xl border border-teal-600 px-5 py-2.5 text-sm font-semibold text-teal-700 transition hover:bg-teal-50"
          >
            Restart
          </button>
        </div>
      </div>
    </section>
  );
}

export default Page3Decision;
