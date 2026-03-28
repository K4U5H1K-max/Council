import { motion } from "framer-motion";
import DecisionPanel from "./DecisionPanel";

function Page3Decision({ finalDecision, onRestart }) {
  return (
    <section className="w-full shrink-0 p-6 sm:p-8 lg:p-10 animate-floatIn">
      <div className="space-y-8">
        <div className="rounded-3xl border border-maroon/25 bg-white p-7 shadow-panel ring-1 ring-maroon/10">
          <h2 className="text-4xl font-bold text-maroon sm:text-5xl">Final Decision</h2>
          <p className="mt-3 text-lg text-maroon/75">
            Consolidated decision and relationship memory after simulation.
          </p>
        </div>

        <DecisionPanel finalDecision={finalDecision} />

        <div className="flex justify-end">
          <motion.button
            type="button"
            whileTap={{ scale: 0.98 }}
            whileHover={{ scale: 1.02 }}
            onClick={onRestart}
            className="rounded-2xl border border-maroon px-7 py-3.5 text-lg font-semibold text-maroon transition duration-300 hover:bg-maroon/5 hover:shadow-sm"
          >
            Restart
          </motion.button>
        </div>
      </div>
    </section>
  );
}

export default Page3Decision;
