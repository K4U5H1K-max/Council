import { motion } from "framer-motion";

const steps = ["Input", "Agents", "Decision"];

function StepIndicator({ step, onStepClick, canOpenAgents, canOpenDecision, completed }) {
  return (
    <div className="rounded-full border border-maroon/20 bg-white/90 px-6 py-4 text-center shadow-sm backdrop-blur">
      <div className="flex items-center justify-center gap-4 text-base text-maroon/70">
        {steps.map((label, index) => {
          const isActive = index === step;
          const isClickable =
            index === 0 || (index === 1 && canOpenAgents) || (index === 2 && canOpenDecision);
          const isCompleted =
            (index === 0 && completed?.input) ||
            (index === 1 && completed?.agents) ||
            (index === 2 && completed?.decision);

          return (
            <div key={label} className="flex items-center gap-4">
              <motion.button
                type="button"
                initial={false}
                animate={{ scale: isActive ? 1.12 : 1 }}
                transition={{ duration: 0.28 }}
                onClick={() => onStepClick?.(index)}
                disabled={!isClickable}
                className={`cursor-pointer rounded-full px-3 py-1 text-base font-semibold transition duration-300 ${
                  isActive
                    ? "bg-maroon text-ivory"
                    : isClickable
                      ? "text-maroon hover:bg-maroon/10"
                      : "cursor-not-allowed text-maroon/35"
                }`}
              >
                {isCompleted ? "✓" : isActive ? "●" : "○"} {label}
              </motion.button>
              {index < steps.length - 1 ? <span className="text-maroon/45">→</span> : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default StepIndicator;
