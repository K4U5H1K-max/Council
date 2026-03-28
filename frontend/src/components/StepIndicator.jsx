function StepIndicator({ step }) {
  return (
    <div className="flex items-center justify-center gap-3 rounded-xl border border-slate-200 bg-white/80 px-4 py-3 shadow-sm backdrop-blur animate-floatIn">
      {[0, 1, 2].map((index) => {
        const isActive = index === step;
        return (
          <span
            key={index}
            className={`h-3 w-3 rounded-full transition-all duration-300 ${
              isActive ? "bg-teal-600 scale-110" : "bg-slate-300"
            }`}
            aria-label={`Step ${index + 1}`}
          />
        );
      })}
    </div>
  );
}

export default StepIndicator;
