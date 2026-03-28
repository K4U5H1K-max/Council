import { motion } from "framer-motion";

function SearchBar({ value, onChange, onSubmit, disabled, submitted, inputDisabled }) {
  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(event);
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={false}
      animate={{ y: submitted ? -26 : 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="w-full"
    >
      <div className="group flex items-center rounded-full border border-maroon/25 bg-white px-5 py-3 shadow-[0_10px_24px_-14px_rgba(90,0,21,0.55)] transition duration-300 focus-within:shadow-[0_14px_30px_-14px_rgba(90,0,21,0.65)]">
        <svg
          viewBox="0 0 24 24"
          aria-hidden="true"
          className="mr-4 h-6 w-6 text-maroon/70"
        >
          <path
            fill="currentColor"
            d="M10.5 3a7.5 7.5 0 0 1 5.97 12.04l4.24 4.24a1 1 0 0 1-1.42 1.42l-4.24-4.24A7.5 7.5 0 1 1 10.5 3Zm0 2a5.5 5.5 0 1 0 0 11a5.5 5.5 0 0 0 0-11Z"
          />
        </svg>

        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Enter your dilemma..."
          disabled={inputDisabled}
          className={`w-full bg-transparent py-2 text-lg outline-none ${
            inputDisabled
              ? "cursor-not-allowed text-maroon/35 placeholder:text-maroon/20"
              : "text-maroon placeholder:text-maroon/50"
          }`}
          aria-label="Dilemma input"
        />

        <motion.button
          type="submit"
          whileTap={{ scale: disabled ? 1 : 0.97 }}
          whileHover={{ scale: disabled ? 1 : 1.02 }}
          disabled={disabled || inputDisabled}
          className="ml-4 rounded-full bg-maroon px-7 py-3 text-lg font-semibold text-ivory transition duration-300 hover:bg-maroonAccent disabled:cursor-not-allowed disabled:opacity-50"
        >
          Go
        </motion.button>
      </div>
    </motion.form>
  );
}

export default SearchBar;
