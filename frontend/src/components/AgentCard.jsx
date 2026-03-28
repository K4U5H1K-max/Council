import { motion } from "framer-motion";

const colorClassMap = {
  blue: {
    shell: "border-blue-200/80 bg-blue-50",
    badge: "border-blue-200 bg-blue-100 text-blue-800",
    icon: "bg-blue-100 text-blue-800",
    glow: "shadow-blue-100",
  },
  red: {
    shell: "border-red-200/80 bg-red-50",
    badge: "border-red-200 bg-red-100 text-red-800",
    icon: "bg-red-100 text-red-800",
    glow: "shadow-red-100",
  },
  green: {
    shell: "border-green-200/80 bg-green-50",
    badge: "border-green-200 bg-green-100 text-green-800",
    icon: "bg-green-100 text-green-800",
    glow: "shadow-green-100",
  },
  pink: {
    shell: "border-pink-200/80 bg-pink-50",
    badge: "border-pink-200 bg-pink-100 text-pink-800",
    icon: "bg-pink-100 text-pink-800",
    glow: "shadow-pink-100",
  },
  gray: {
    shell: "border-slate-200 bg-slate-50",
    badge: "border-slate-200 bg-slate-100 text-slate-800",
    icon: "bg-slate-200 text-slate-800",
    glow: "shadow-slate-200",
  },
  yellow: {
    shell: "border-yellow-200/80 bg-yellow-50",
    badge: "border-yellow-200 bg-yellow-100 text-yellow-800",
    icon: "bg-yellow-100 text-yellow-800",
    glow: "shadow-yellow-100",
  },
  purple: {
    shell: "border-violet-200/80 bg-violet-50",
    badge: "border-violet-200 bg-violet-100 text-violet-800",
    icon: "bg-violet-100 text-violet-800",
    glow: "shadow-violet-100",
  },
  default: {
    shell: "border-slate-200 bg-slate-50",
    badge: "border-slate-200 bg-slate-100 text-slate-700",
    icon: "bg-slate-200 text-slate-700",
    glow: "shadow-slate-200",
  },
};

function AgentCard({ agent }) {
  const colors = colorClassMap[agent.theme] || colorClassMap.default;
  const personality = agent.tags[0] || "Balanced";

  return (
    <motion.article
      title={agent.tooltip || `${agent.name} perspective`}
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.2 }}
      className={`rounded-2xl border p-4 shadow-sm transition duration-300 hover:shadow-lg ${colors.shell} ${colors.glow}`}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${colors.icon}`}>
            {agent.icon || agent.name.slice(0, 1)}
          </span>
          <h3 className="text-base font-semibold text-slate-900">{agent.name}</h3>
        </div>
        <span className="rounded-lg bg-white/80 px-2 py-1 text-xs font-medium text-slate-600">
          #{agent.id}
        </span>
      </div>

      <div className="mt-3">
        <span className={`rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${colors.badge}`}>
          Personality: {personality}
        </span>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {agent.tags.map((tag) => (
          <span
            key={tag}
            className={`rounded-full border px-2.5 py-1 text-xs font-medium ${colors.badge}`}
          >
            {tag}
          </span>
        ))}
      </div>

      <p className="mt-4 text-sm leading-relaxed text-slate-700">{agent.proposal}</p>
    </motion.article>
  );
}

export default AgentCard;
