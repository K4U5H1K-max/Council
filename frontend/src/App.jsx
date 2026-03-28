import { useState } from "react";
import MainContainer from "./components/MainContainer";
import StepIndicator from "./components/StepIndicator";
import Page1Input from "./components/Page1Input";
import Page2Agents from "./components/Page2Agents";
import Page3Decision from "./components/Page3Decision";
import { agentConfigs, useCaseLabels } from "./config/agentConfigs";

const proposalFragments = {
  Rational: "a logical approach with explicit trade-offs and measurable checkpoints",
  Ambitious: "a bold expansion play to maximize upside and strategic momentum",
  Conservative: "a guarded path that limits downside while preserving flexibility",
  Emotional: "a people-first direction that protects wellbeing and relationships",
  Realist: "a practical route with clear constraints, costs, and execution realities",
  Optimist: "a positive outlook that leverages momentum and compounding benefits",
  Pessimist: "a cautious stress-tested plan that anticipates failure points",
};

const buildAgentProposal = (agentName, userInput, useCase) => {
  const core = proposalFragments[agentName] || "a balanced strategy aligned to the context";
  const contextNote =
    userInput.trim().length > 0
      ? ` Context: ${userInput.trim().slice(0, 110)}${userInput.trim().length > 110 ? "..." : ""}`
      : "";

  return `${agentName} suggests ${core} for this ${useCase === "scenario" ? "scenario" : "consult"}.${contextNote}`;
};

const buildAgents = (useCase, userInput) =>
  (agentConfigs[useCase] || []).map((agent, index) => ({
    id: `A${index + 1}`,
    name: agent.name,
    theme: agent.color,
    tags: agent.traits,
    proposal: buildAgentProposal(agent.name, userInput, useCase),
    icon: agent.icon,
    tooltip: agent.tooltip,
  }));

const buildDebate = (agents) => {
  if (!agents.length) return [];

  const critiques = agents.map((agent, index) => {
    const target = agents[(index + 1) % agents.length];
    return {
      id: `M${index + 1}`,
      agent: agent.name,
      text: `${agent.name} questions ${target.name}'s assumptions and requests stronger evidence before full commitment.`,
    };
  });

  return [
    ...critiques,
    {
      id: `M${agents.length + 1}`,
      agent: agents[0].name,
      text: "Working consensus: proceed in stages with explicit guardrails and shared review checkpoints.",
    },
  ];
};

const buildTrustMatrix = (agents) => {
  const matrix = {};

  agents.forEach((fromAgent, fromIndex) => {
    matrix[fromAgent.name] = {};

    agents.forEach((toAgent, toIndex) => {
      if (fromIndex === toIndex) {
        matrix[fromAgent.name][toAgent.name] = 1;
        return;
      }

      const score = 0.48 + (((fromIndex + 2) * (toIndex + 3)) % 5) * 0.1;
      matrix[fromAgent.name][toAgent.name] = Number(score.toFixed(2));
    });
  });

  return matrix;
};

const buildFinalDecision = (useCase, agents, userInput) => ({
  text:
    useCase === "scenario"
      ? `Scenario verdict: start with a bounded experiment, monitor leading indicators weekly, and scale only after threshold outcomes are met.${
          userInput.trim() ? ` Core prompt: ${userInput.trim().slice(0, 95)}...` : ""
        }`
      : `Personal consult verdict: choose the option that keeps upside available while protecting stability through phased commitments.${
          userInput.trim() ? ` Core prompt: ${userInput.trim().slice(0, 95)}...` : ""
        }`,
  influencingAgent: agents[0]?.name || "Council",
  confidence: useCase === "scenario" ? 0.86 : 0.9,
});

function App() {
  const [step, setStep] = useState(0);
  const [useCase, setUseCase] = useState("personal");
  const [userInput, setUserInput] = useState("");
  const [agents, setAgents] = useState(() => buildAgents("personal", ""));
  const [critiqueMessages, setCritiqueMessages] = useState(() =>
    buildDebate(buildAgents("personal", ""))
  );
  const [trustMatrix, setTrustMatrix] = useState(() => buildTrustMatrix(buildAgents("personal", "")));
  const [finalDecision, setFinalDecision] = useState(() =>
    buildFinalDecision("personal", buildAgents("personal", ""), "")
  );
  const [isLoading, setIsLoading] = useState(false);

  const runSimulation = () => {
    if (isLoading) return;
    setIsLoading(true);

    setTimeout(() => {
      const computedAgents = buildAgents(useCase, userInput);
      setAgents(computedAgents);
      setCritiqueMessages(buildDebate(computedAgents));
      setTrustMatrix(buildTrustMatrix(computedAgents));
      setFinalDecision(buildFinalDecision(useCase, computedAgents, userInput));

      setIsLoading(false);
    }, 900);
  };

  const handleNextFromInput = () => {
    setStep(1);
    runSimulation();
  };

  const handleNextFromAgents = () => setStep(2);

  const handleRestart = () => {
    setStep(0);
    setUserInput("");
    const resetAgents = buildAgents(useCase, "");
    setAgents(resetAgents);
    setCritiqueMessages(buildDebate(resetAgents));
    setTrustMatrix(buildTrustMatrix(resetAgents));
    setFinalDecision(buildFinalDecision(useCase, resetAgents, ""));
    setIsLoading(false);
  };

  return (
    <div className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-8">
      <div className="space-y-5">
        <header className="rounded-2xl border border-teal-100 bg-white/90 p-6 shadow-panel backdrop-blur animate-floatIn">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Council of Agents</h1>
          <p className="mt-1 text-sm text-slate-600">Multi-Agent Decision Intelligence System</p>
        </header>

        <StepIndicator step={step} />

        <MainContainer step={step} totalSteps={3}>
          <Page1Input
            userInput={userInput}
            useCase={useCase}
            onInputChange={setUserInput}
            onUseCaseChange={setUseCase}
            onNext={handleNextFromInput}
            isLoading={isLoading}
          />

          <Page2Agents
            agents={agents}
            critiqueMessages={critiqueMessages}
            useCaseLabel={useCaseLabels[useCase]}
            useCase={useCase}
            onNext={handleNextFromAgents}
            isLoading={isLoading}
          />

          <Page3Decision
            finalDecision={finalDecision}
            trustMatrix={trustMatrix}
            onRestart={handleRestart}
          />
        </MainContainer>

        <div className="rounded-xl border border-slate-200 bg-white/80 px-4 py-2 text-center text-xs text-slate-500">
          Step {step + 1} of 3
        </div>
      </div>
    </div>
  );
}

export default App;
