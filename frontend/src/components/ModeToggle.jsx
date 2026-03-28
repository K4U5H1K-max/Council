import { motion } from "framer-motion";

function ModeToggle({ mode, onModeChange, disabled }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28, delay: 0.08 }}
      className="inline-flex rounded-full border border-maroon/25 bg-white p-1.5 shadow-sm"
      role="tablist"
      aria-label="Mode toggle"
    >
      {[
        { key: "practical", label: "Practical" },
        { key: "creative", label: "Creative" },
      ].map((item) => {
        const isActive = mode === item.key;
        return (
          <button
            key={item.key}
            type="button"
            onClick={() => onModeChange(item.key)}
            disabled={disabled}
            className={`rounded-full px-7 py-3 text-lg font-semibold transition-all duration-300 ${
              disabled
                ? "cursor-not-allowed text-maroon/35 opacity-50"
                : isActive
                  ? "bg-maroon text-ivory shadow"
                  : "text-maroon/75 hover:bg-maroon/5"
            }`}
          >
            {item.label}
          </button>
        );
      })}
    </motion.div>
  );
}

export default ModeToggle;
