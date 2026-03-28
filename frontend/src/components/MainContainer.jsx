import { Children } from "react";
import { AnimatePresence, motion } from "framer-motion";

function MainContainer({ step, children }) {
  const pages = Children.toArray(children);

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white/70 shadow-panel backdrop-blur">
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={step}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -16 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
        >
          {pages[step]}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export default MainContainer;
