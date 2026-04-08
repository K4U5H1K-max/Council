export const useCaseOptions = [
  { value: "debate", label: "Battle of the Bots" },
];

export const useCaseLabels = {
  debate: "Battle of the Bots",
};

export const agentConfigs = {
  debate: [
    {
      name: "Pro Agent",
      traits: ["Supportive", "Persuasive"],
      color: "blue",
      icon: "P",
      tooltip: "Argues in favor of the topic with structured supporting points.",
    },
    {
      name: "Con Agent",
      traits: ["Critical", "Analytical"],
      color: "red",
      icon: "C",
      tooltip: "Argues against the topic with counterarguments and trade-offs.",
    },
    {
      name: "Evaluator Agent",
      traits: ["Objective", "Comparative"],
      color: "gray",
      icon: "E",
      tooltip: "Questions both sides each round and issues final judgement.",
    },
  ],
};
