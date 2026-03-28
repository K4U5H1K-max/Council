import AgentCard from "./AgentCard";

function AgentGrid({ agents, useCase }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-panel backdrop-blur animate-floatIn">
      <h2 className="text-lg font-semibold text-slate-900">Agent Proposals</h2>
      <p className="mt-1 text-sm text-slate-600">
        Diverse agents generate distinct response strategies.
      </p>

      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4" key={useCase}>
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </section>
  );
}

export default AgentGrid;
