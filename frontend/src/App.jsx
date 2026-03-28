import { useCallback, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import LandingContainer from "./components/LandingContainer";
import StepIndicator from "./components/StepIndicator";
import PersonalizerDialog from "./components/PersonalizerDialog";
import Page2Agents from "./components/Page2Agents";
import Page3Decision from "./components/Page3Decision";
import { agentConfigs } from "./config/agentConfigs";

const API_CANDIDATES = [
  "http://127.0.0.1:8000/api",
  "/api",
];

const IRRELEVANT_OPERATION_PATTERNS = [
  /\bwrite\s+code\b/i,
  /\bbuild\s+(an\s+)?app\b/i,
  /\bcreate\s+(a\s+)?website\b/i,
  /\bdebug\s+(my\s+)?code\b/i,
  /\bfix\s+(the\s+)?bug\b/i,
  /\brun\s+(a\s+)?command\b/i,
  /\bopen\s+(the\s+)?browser\b/i,
  /\bsend\s+(an\s+)?email\b/i,
  /\bdownload\s+(a\s+)?file\b/i,
];

const DECISION_CONTEXT_HINTS = [
  " i ",
  " my ",
  " me ",
  "learn",
  "study",
  "career",
  "relationship",
  "health",
  "goal",
  "habit",
  "decision",
  "choose",
  "plan",
  "strategy",
  "what if",
  "should",
];

const validateUserPrompt = (query) => {
  const text = String(query || "").trim();
  if (!text) {
    return "Please enter a scenario or question.";
  }

  const lowered = ` ${text.toLowerCase()} `;
  const isOperational = IRRELEVANT_OPERATION_PATTERNS.some((pattern) => pattern.test(lowered));
  const hasDecisionContext = DECISION_CONTEXT_HINTS.some((hint) => lowered.includes(hint));

  if (isOperational && !hasDecisionContext) {
    return "This looks like an operational task request. Please rephrase it as a scenario or decision you want guidance on.";
  }

  return "";
};

const fetchPersonalizerQuestions = async (mode, query) => {
  let lastError = null;

  for (const base of API_CANDIDATES) {
    try {
      const response = await fetch(`${base}/personalizer/questions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, query }),
      });

      if (!response.ok) {
        let errorText = `HTTP ${response.status}`;
        try {
          const errorPayload = await response.json();
          if (typeof errorPayload?.error === "string" && errorPayload.error.trim()) {
            errorText = errorPayload.error;
          }
        } catch {
          // Keep fallback status message when JSON parsing fails.
        }
        throw new Error(errorText);
      }

      return await response.json();
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error("Failed to fetch personalizer questions");
};

const fetchWorkflowRun = async (mode, query, additionalInfo = []) => {
  let lastError = null;

  for (const base of API_CANDIDATES) {
    try {
      const response = await fetch(`${base}/workflow/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, query, additional_info: additionalInfo }),
      });

      if (!response.ok) {
        let errorText = `HTTP ${response.status}`;
        try {
          const errorPayload = await response.json();
          if (typeof errorPayload?.error === "string" && errorPayload.error.trim()) {
            errorText = errorPayload.error;
          }
        } catch {
          // Keep fallback status message when JSON parsing fails.
        }
        throw new Error(errorText);
      }

      return await response.json();
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error("Failed to run council workflow");
};

const mapTranscriptToChatAgents = (transcript, useCase) => {
  const configByName = new Map(
    (agentConfigs[useCase] || []).map((cfg, index) => [cfg.name.toLowerCase(), { ...cfg, index }])
  );

  return (Array.isArray(transcript) ? transcript : []).map((entry, index) => {
    const displayName = entry.agent_display || String(entry.agent || "Agent").replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
    const lookup = displayName.toLowerCase();
    const cfg = configByName.get(lookup) || configByName.get("ambitious");

    return {
      id: `A-${index + 1}`,
      name: displayName,
      theme: cfg?.color || "gray",
      tags: cfg?.traits || [],
      proposal: entry.response || "",
      icon: cfg?.icon || displayName.slice(0, 1),
      tooltip: cfg?.tooltip || "",
      exchange: entry.exchange,
    };
  });
};

const mapHistoryToChatAgents = (history, useCase) => {
  if (!history || typeof history !== "object") return [];

  const normalizedNames = Object.keys(history);
  const roundsByAgent = normalizedNames.map((name) => ({
    name,
    responses: Array.isArray(history[name]) ? history[name] : [],
  }));

  const maxRounds = roundsByAgent.reduce(
    (max, entry) => Math.max(max, entry.responses.length),
    0
  );

  const transcriptLike = [];
  for (let round = 0; round < maxRounds; round += 1) {
    for (const agentEntry of roundsByAgent) {
      const response = agentEntry.responses[round];
      if (!response) continue;
      transcriptLike.push({
        exchange: round + 1,
        agent: agentEntry.name,
        response,
      });
    }
  }

  return mapTranscriptToChatAgents(transcriptLike, useCase);
};

function App() {
  const [currentStep, setCurrentStep] = useState(0); // 0=input, 1=agents, 2=decision
  const [mode, setMode] = useState("practical");
  const [inputData, setInputData] = useState("");
  const [personalContext, setPersonalContext] = useState({ q1: "", q2: "" });
  const [personalizerQuestions, setPersonalizerQuestions] = useState([
    "What outcome matters most right now?",
    "What constraint should we avoid?",
  ]);
  const [personalizerMessage, setPersonalizerMessage] = useState(
    "A short profile helps tune the council response."
  );
  const [showPersonalizer, setShowPersonalizer] = useState(false);

  const useCase = mode === "practical" ? "personal" : "scenario";
  const modeLabel = mode === "practical" ? "Practical" : "Creative";

  const [agentResponses, setAgentResponses] = useState([]);
  const [critiqueMessages, setCritiqueMessages] = useState([]);
  const [finalDecision, setFinalDecision] = useState(null);
  const [workflowError, setWorkflowError] = useState("");
  const [inputGuardrailError, setInputGuardrailError] = useState("");
  const [hasPlayedAgentChat, setHasPlayedAgentChat] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const isOutputLocked = Boolean(finalDecision);

  const handleAgentChatPlayed = useCallback(() => {
    setHasPlayedAgentChat(true);
  }, []);

  const invalidateComputedStages = () => {
    setAgentResponses([]);
    setCritiqueMessages([]);
    setFinalDecision(null);
    setWorkflowError("");
    setHasPlayedAgentChat(false);
  };

  const runSimulation = async (nextContext) => {
    if (isLoading) return;
    setIsLoading(true);
    setWorkflowError("");

    try {
      const modeValue = useCase === "personal" ? "personal" : "whatif";
      const additionalInfo = [];

      if (nextContext?.q1?.trim()) {
        additionalInfo.push({ question: "q1", answer: nextContext.q1.trim() });
      }
      if (nextContext?.q2?.trim()) {
        additionalInfo.push({ question: "q2", answer: nextContext.q2.trim() });
      }

      const payload = await fetchWorkflowRun(modeValue, inputData.trim(), additionalInfo);
      const transcript = payload?.conversation?.transcript || [];
      const history = payload?.conversation?.history || {};
      const chatAgents = transcript.length > 0
        ? mapTranscriptToChatAgents(transcript, useCase)
        : mapHistoryToChatAgents(history, useCase);

      if (chatAgents.length === 0) {
        setWorkflowError("Workflow completed but returned no agent messages.");
      }

      setAgentResponses(chatAgents);
      setCritiqueMessages(Array.isArray(payload?.debate) ? payload.debate : []);
      setFinalDecision(payload?.final || null);
      setHasPlayedAgentChat(false);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown workflow error";
      setAgentResponses([]);
      setCritiqueMessages([
        {
          id: "D-error",
          agent: "System",
          text: `Workflow request failed: ${message}`,
        },
      ]);
      setFinalDecision({
        text: `Unable to generate council output right now. ${message}`,
        influencingAgent: "System",
        confidence: 0,
        insights: [
          "Backend request did not complete successfully.",
          "Please verify API server is running and reachable from the frontend.",
        ],
      });
      setWorkflowError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const ensurePipelineData = (context) => {
    if (agentResponses.length === 0) {
      runSimulation(context);
      return;
    }
  };

  const requiredAnswers = Math.max(1, Math.min(2, personalizerQuestions.length || 0));
  const canOpenAgents =
    mode === "creative"
      ? Boolean(inputData.trim())
      : requiredAnswers === 1
        ? Boolean(inputData.trim() && personalContext.q1?.trim())
        : Boolean(inputData.trim() && personalContext.q1?.trim() && personalContext.q2?.trim());
  const canOpenDecision = canOpenAgents && agentResponses.length > 0;

  const handleStepNavigation = (targetStep) => {
    if (targetStep === 0) {
      setCurrentStep(0);
      return;
    }

    if (targetStep === 1) {
      if (!canOpenAgents) return;
      setCurrentStep(1);
      ensurePipelineData(personalContext);
      return;
    }

    if (targetStep === 2) {
      if (!canOpenDecision) return;
      setCurrentStep(2);
    }
  };

  const handleInputSubmit = async (event) => {
    event.preventDefault();
    if (!inputData.trim()) return;

    const guardrailError = validateUserPrompt(inputData);
    if (guardrailError) {
      setInputGuardrailError(guardrailError);
      setShowPersonalizer(false);
      setCurrentStep(0);
      return;
    }

    setInputGuardrailError("");

    const modeValue = mode === "practical" ? "personal" : "whatif";

    if (modeValue === "whatif") {
      setShowPersonalizer(false);
      setCurrentStep(1);
      runSimulation({ q1: "", q2: "" });
      return;
    }

    try {
      const payload = await fetchPersonalizerQuestions(modeValue, inputData.trim());
      const questions = Array.isArray(payload.questions) ? payload.questions.slice(0, 2) : [];

      setPersonalizerQuestions(
        questions.length > 0
          ? questions
          : ["Any additional details you want the council to consider?"]
      );
      setPersonalizerMessage(
        payload.message || "A short profile helps tune the council response."
      );
    } catch (error) {
      setPersonalizerQuestions([
        "What outcome matters most right now?",
        "What constraint should we avoid?",
      ]);
      setPersonalizerMessage(
        "Backend question service is unavailable. Showing default prompts."
      );
    }

    setShowPersonalizer(true);
  };

  const handleContinueFromPersonalizer = () => {
    if (!personalContext.q1?.trim()) return;
    if (personalizerQuestions.length > 1 && !personalContext.q2?.trim()) return;
    const nextContext = { q1: personalContext.q1, q2: personalContext.q2 };
    setShowPersonalizer(false);
    setCurrentStep(1);
    runSimulation(nextContext);
  };

  const handleNextFromAgents = () => {
    if (!finalDecision) return;
    setCurrentStep(2);
  };

  const handleRestart = () => {
    setCurrentStep(0);
    setInputData("");
    setPersonalContext({ q1: "", q2: "" });
    setPersonalizerQuestions([
      "What outcome matters most right now?",
      "What constraint should we avoid?",
    ]);
    setPersonalizerMessage("A short profile helps tune the council response.");
    setShowPersonalizer(false);
    invalidateComputedStages();
    setIsLoading(false);
  };

  const handleInputChange = (value) => {
    setInputData(value);
    if (inputGuardrailError) {
      setInputGuardrailError("");
    }
    invalidateComputedStages();
  };

  const handleModeChange = (nextMode) => {
    setMode(nextMode);
    setShowPersonalizer(false);
    setPersonalContext({ q1: "", q2: "" });
    setPersonalizerQuestions([
      "What outcome matters most right now?",
      "What constraint should we avoid?",
    ]);
    setPersonalizerMessage("A short profile helps tune the council response.");
    invalidateComputedStages();
  };

  const handlePersonalContextChange = (key, value) => {
    setPersonalContext((previous) => ({ ...previous, [key]: value }));
    invalidateComputedStages();
  };

  const completed = {
    input: canOpenAgents,
    agents: agentResponses.length > 0,
    decision: Boolean(finalDecision),
  };

  return (
    <div className="min-h-screen bg-ivory px-4 py-8 text-maroon sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col items-center">
        <div className="mx-auto mb-8 w-full max-w-4xl">
          {inputGuardrailError ? (
            <div className="mb-3 rounded-xl border border-amber-300 bg-amber-50 px-4 py-2 text-sm text-amber-900">
              {inputGuardrailError}
            </div>
          ) : null}
          {workflowError ? (
            <div className="mb-3 rounded-xl border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-800">
              Backend workflow error: {workflowError}
            </div>
          ) : null}
          <StepIndicator
            step={currentStep}
            onStepClick={handleStepNavigation}
            canOpenAgents={canOpenAgents}
            canOpenDecision={canOpenDecision}
            completed={completed}
          />
        </div>

        <AnimatePresence mode="wait">
          {currentStep === 0 ? (
            <motion.div
              key="input-sequence"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.35 }}
              className="w-full"
            >
              <LandingContainer
                mode={mode}
                onModeChange={handleModeChange}
                userInput={inputData}
                onInputChange={handleInputChange}
                onSubmit={handleInputSubmit}
                submitted={showPersonalizer}
                isReadOnly={isOutputLocked}
              />

              {showPersonalizer ? (
                <PersonalizerDialog
                  q1Answer={personalContext.q1 || ""}
                  q2Answer={personalContext.q2 || ""}
                  questions={personalizerQuestions}
                  message={personalizerMessage}
                  onQ1Change={(value) => handlePersonalContextChange("q1", value)}
                  onQ2Change={(value) => handlePersonalContextChange("q2", value)}
                  onContinue={handleContinueFromPersonalizer}
                />
              ) : null}
            </motion.div>
          ) : currentStep === 1 ? (
            <motion.div
              key="agents-sequence"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.35 }}
              className="w-full"
            >
              <Page2Agents
                agents={agentResponses}
                critiqueMessages={critiqueMessages}
                useCaseLabel={modeLabel}
                useCase={useCase}
                hasPlayed={hasPlayedAgentChat}
                onPlayed={handleAgentChatPlayed}
                onNext={handleNextFromAgents}
                isLoading={isLoading}
              />
            </motion.div>
          ) : (
            <motion.div
              key="decision-sequence"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.35 }}
              className="w-full"
            >
              <Page3Decision
                finalDecision={finalDecision}
                onRestart={handleRestart}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
