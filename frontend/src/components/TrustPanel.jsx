function TrustPanel({ trustMatrix }) {
  const agentNames = Object.keys(trustMatrix);

  const scoreToClass = (score) => {
    if (score >= 0.75) return "bg-emerald-100 text-emerald-700";
    if (score >= 0.5) return "bg-amber-100 text-amber-700";
    return "bg-rose-100 text-rose-700";
  };

  return (
    <section className="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-panel backdrop-blur animate-floatIn">
      <h2 className="text-lg font-semibold text-slate-900">Trust Network</h2>
      <p className="mt-1 text-sm text-slate-600">
        Matrix view of inter-agent trust scores.
      </p>

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-y-2 text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
              <th className="px-2 py-1">From / To</th>
              {agentNames.map((name) => (
                <th key={name} className="px-2 py-1">
                  {name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {agentNames.map((fromName) => (
              <tr key={fromName}>
                <td className="px-2 py-1 font-medium text-slate-800">{fromName}</td>
                {agentNames.map((toName) => {
                  const score = trustMatrix[fromName][toName];
                  return (
                    <td key={`${fromName}-${toName}`} className="px-2 py-1">
                      <span className={`inline-flex min-w-14 justify-center rounded-lg px-2 py-1 font-semibold ${scoreToClass(score)}`}>
                        {score.toFixed(2)}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default TrustPanel;
