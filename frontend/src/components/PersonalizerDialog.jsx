import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

function PersonalizerDialog({ q1Answer, q2Answer, questions = [], message, onQ1Change, onQ2Change, onContinue }) {
  const q1Label = questions[0] || "What outcome matters most right now?";
  const q2Label = questions[1] || "What constraint should we avoid?";
  const hasSecondQuestion = questions.length > 1;
  const [showQ2, setShowQ2] = useState(Boolean(q1Answer.trim()));

  const canRevealQ2 = q1Answer.trim().length > 0;
  const canContinue = useMemo(() => {
    if (!q1Answer.trim()) return false;
    if (!hasSecondQuestion) return true;
    return q2Answer.trim().length > 0;
  }, [q1Answer, q2Answer, hasSecondQuestion]);

  const handleQ1Submit = (event) => {
    event.preventDefault();
    if (!canRevealQ2) return;
    setShowQ2(true);
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="mx-auto mt-10 w-full max-w-3xl rounded-3xl border border-maroon/25 bg-white p-8 shadow-[0_16px_38px_-24px_rgba(90,0,21,0.65)]"
    >
      <h2 className="text-center text-3xl font-bold text-maroon">Personal Context</h2>
      <p className="mt-2 text-center text-lg text-maroon/75">{message || "A short profile helps tune the council response."}</p>

      <form className="mt-7 space-y-5" onSubmit={handleQ1Submit}>
        <label className="block text-lg font-medium text-maroon">
          {q1Label}
          <input
            type="text"
            value={q1Answer}
            onChange={(event) => onQ1Change(event.target.value)}
            className="mt-3 w-full rounded-2xl border border-maroon/25 bg-ivory px-4 py-3 text-lg text-maroon outline-none ring-maroon/25 transition focus:ring"
            placeholder="Example: Preserve stability while progressing"
          />
        </label>

        {!showQ2 && hasSecondQuestion ? (
          <motion.button
            type="submit"
            whileTap={{ scale: 0.98 }}
            whileHover={{ scale: 1.02 }}
            disabled={!canRevealQ2}
            className="rounded-2xl bg-maroon px-7 py-3 text-lg font-semibold text-ivory transition duration-300 hover:bg-maroonAccent disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
          </motion.button>
        ) : null}

        {!hasSecondQuestion ? (
          <motion.button
            type="button"
            whileTap={{ scale: 0.98 }}
            whileHover={{ scale: 1.02 }}
            disabled={!canContinue}
            onClick={onContinue}
            className="rounded-2xl bg-maroon px-8 py-3 text-lg font-semibold text-ivory transition duration-300 hover:bg-maroonAccent disabled:cursor-not-allowed disabled:opacity-50"
          >
            Continue
          </motion.button>
        ) : null}
      </form>

      <AnimatePresence>
        {showQ2 && hasSecondQuestion ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.3 }}
            className="mt-5"
          >
            <label className="block text-lg font-medium text-maroon">
              {q2Label}
              <input
                type="text"
                value={q2Answer}
                onChange={(event) => onQ2Change(event.target.value)}
                className="mt-3 w-full rounded-2xl border border-maroon/25 bg-ivory px-4 py-3 text-lg text-maroon outline-none ring-maroon/25 transition focus:ring"
                placeholder="Example: Team burnout or budget overrun"
              />
            </label>

            <motion.button
              type="button"
              whileTap={{ scale: 0.98 }}
              whileHover={{ scale: 1.02 }}
              disabled={!canContinue}
              onClick={onContinue}
              className="mt-5 rounded-2xl bg-maroon px-8 py-3 text-lg font-semibold text-ivory transition duration-300 hover:bg-maroonAccent disabled:cursor-not-allowed disabled:opacity-50"
            >
              Continue
            </motion.button>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </motion.section>
  );
}

export default PersonalizerDialog;
