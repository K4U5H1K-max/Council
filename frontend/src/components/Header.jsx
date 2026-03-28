function Header({ onRunSimulation, isLoading }) {
  return (
    <header className="rounded-2xl border border-teal-100 bg-white/90 p-6 shadow-panel backdrop-blur">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Council of Agents
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Multi-Agent Decision Intelligence System
          </p>
        </div>
        <button
          type="button"
          onClick={onRunSimulation}
          disabled={isLoading}
          className="inline-flex items-center justify-center rounded-xl bg-teal-600 px-5 py-3 text-sm font-semibold text-white shadow transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isLoading ? "Running..." : "Run Simulation"}
        </button>
      </div>
    </header>
  );
}

export default Header;
