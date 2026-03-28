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
        Council of Agents
      </h1>
      <p className="mt-4 text-lg text-maroon/80 sm:text-xl">
        Multi-Agent Decision Intelligence System
      </p>
    </motion.header>
  );
}

export default Header;
