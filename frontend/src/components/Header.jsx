import { motion } from "framer-motion";

function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32 }}
      className="text-center"
    >
      <h1 className="text-5xl font-extrabold tracking-tight text-maroon sm:text-6xl lg:text-7xl">
        Battle of the Bots
      </h1>
      <p className="mt-4 text-lg text-maroon/80 sm:text-xl">
        Pro vs Con with Evaluator-led 3-round debate
      </p>
    </motion.header>
  );
}

export default Header;
