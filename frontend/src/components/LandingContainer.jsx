import { motion } from "framer-motion";
import Header from "./Header";
import SearchBar from "./SearchBar";

function LandingContainer({
  userInput,
  onInputChange,
  onSubmit,
  submitted,
  isReadOnly,
}) {
  const disabledSubmit = !userInput.trim() || isReadOnly;

  return (
    <section className={`mx-auto flex w-full max-w-5xl flex-col items-center px-4 ${submitted ? "pt-12" : "pt-24 sm:pt-28"}`}>
      <motion.div
        initial="hidden"
        animate="show"
        variants={{
          hidden: {},
          show: {
            transition: {
              staggerChildren: 0.1,
            },
          },
        }}
        className="w-full text-center"
      >
        <motion.div variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }}>
          <Header />
        </motion.div>

        <motion.div
          variants={{ hidden: { opacity: 0, y: 14 }, show: { opacity: 1, y: 0 } }}
          className="mx-auto mt-12 w-full max-w-3xl"
        >
          <SearchBar
            value={userInput}
            onChange={onInputChange}
            onSubmit={onSubmit}
            disabled={disabledSubmit}
            submitted={submitted}
            inputDisabled={isReadOnly}
          />
        </motion.div>
      </motion.div>
    </section>
  );
}

export default LandingContainer;
