import ChatContainer from "./ChatContainer";

function AgentGrid({ agents, useCase, isLoading, hasPlayed, onPlayed }) {
  return (
    <section className="rounded-3xl border border-maroon/20 bg-white/90 p-7 shadow-panel backdrop-blur animate-floatIn">
      <h2 className="text-3xl font-bold text-maroon">Agent Conversation</h2>
      <p className="mt-2 text-lg text-maroon/75">
        Agents respond one-by-one in a conversational flow.
      </p>

      <ChatContainer
        agents={agents}
        useCase={useCase}
        isLoading={isLoading}
        hasPlayed={hasPlayed}
        onPlayed={onPlayed}
      />
    </section>
  );
}

export default AgentGrid;
