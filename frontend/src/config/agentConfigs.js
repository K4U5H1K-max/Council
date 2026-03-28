export const useCaseOptions = [
  { value: "personal", label: "Practical — Personal Consult" },
  { value: "scenario", label: "Creative — What If Scenario" },
];

export const useCaseLabels = {
  personal: "Practical — Personal Consult",
  scenario: "Creative — What If Scenario",
};

export const agentConfigs = {
  personal: [
    {
      name: "Rational",
      traits: ["Logical", "Risk-aware"],
      color: "blue",
      icon: "R",
      tooltip: "Prioritizes evidence, structure, and clear trade-offs.",
    },
    {
      name: "Ambitious",
      traits: ["Growth-driven", "Aggressive"],
      color: "red",
      icon: "A",
      tooltip: "Pushes for upside and speed, even with higher uncertainty.",
    },
    {
      name: "Conservative",
      traits: ["Safe", "Stable"],
      color: "green",
      icon: "C",
      tooltip: "Protects downside and prefers gradual, resilient progress.",
    },
    {
      name: "Emotional",
      traits: ["Empathetic", "Intuitive"],
      color: "pink",
      icon: "E",
      tooltip: "Centers people impact, values, and human consequences.",
    },
  ],
  scenario: [
    {
      name: "Realist",
      traits: ["Practical", "Grounded"],
      color: "gray",
      icon: "R",
      tooltip: "Keeps recommendations realistic and execution-aware.",
    },
    {
      name: "Ambitious",
      traits: ["Expansion-focused", "Bold"],
      color: "red",
      icon: "A",
      tooltip: "Looks for leverage and breakthrough opportunities.",
    },
    {
      name: "Optimist",
      traits: ["Positive", "Hopeful"],
      color: "yellow",
      icon: "O",
      tooltip: "Highlights upside potential and momentum effects.",
    },
    {
      name: "Pessimist",
      traits: ["Critical", "Risk-focused"],
      color: "purple",
      icon: "P",
      tooltip: "Stress-tests assumptions and surfaces hidden failure modes.",
    },
  ],
};
