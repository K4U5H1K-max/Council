import { useState } from "react";
import { motion } from "framer-motion";
import AgentGrid from "./AgentGrid";
import DebatePanel from "./DebatePanel";

function Page2Agents({
  agents,
  critiqueMessages,
  useCaseLabel,
  useCase,
  hasPlayed,
  onPlayed,
  onNext,
  isLoading,
}) {
  const [showDebate, setShowDebate] = useState(false);
  const modeLabel = useCaseLabel;

  return (
    <section className="w-full shrink-0 p-6 sm:p-8 lg:p-10 animate-floatIn">
      <div className="space-y-8">
        <div className="rounded-3xl border border-maroon/20 bg-white p-6 shadow-sm">
          <h2 className="text-3xl font-bold text-maroon">Agent Interaction</h2>
          <p className="mt-2 text-lg text-maroon/75">
            Evaluator questions and Pro/Con defenses run through 3 structured rounds.
          </p>

          <motion.p
            key={modeLabel}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-4 inline-flex rounded-full border border-maroon/25 bg-maroon/5 px-4 py-2 text-base font-semibold text-maroon"
          >
            Mode: {modeLabel}
          </motion.p>

          <p className="mt-3 text-base text-maroon/65">Single debate mode with round-by-round reasoning.</p>

          {isLoading ? (
            <p className="mt-4 text-lg font-medium text-maroon/85">Agents are thinking...</p>
          ) : null}
        </div>

        <AgentGrid
          agents={agents}
          useCase={useCase}
          isLoading={isLoading}
          hasPlayed={hasPlayed}
          onPlayed={onPlayed}
        />

        <div className="flex items-center justify-between gap-2">
          <motion.button
            type="button"
            whileTap={{ scale: 0.98 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => setShowDebate((previous) => !previous)}
            className="rounded-2xl border border-maroon/25 bg-white px-6 py-3 text-base font-semibold text-maroon transition duration-300 hover:bg-maroon/5"
          >
            {showDebate ? "Hide Debate Summary" : "Show Debate Summary"}
          </motion.button>
          <p className="text-base text-maroon/65">Latest Pro, Con, and Evaluator final insight</p>
        </div>

        {showDebate ? <DebatePanel messages={critiqueMessages} isLoading={isLoading} /> : null}

        <div className="flex justify-end">
          <motion.button
            type="button"
            whileTap={{ scale: 0.98 }}
            whileHover={{ scale: 1.02 }}
            onClick={onNext}
            disabled={isLoading}
            className="rounded-2xl bg-maroon px-7 py-3.5 text-lg font-semibold text-ivory transition duration-300 hover:bg-maroonAccent hover:shadow-md disabled:cursor-not-allowed disabled:opacity-60"
          >
            Next
          </motion.button>
        </div>
      </div>
    </section>
  );
}

export default Page2Agents;
