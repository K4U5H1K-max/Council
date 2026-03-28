import { Children } from "react";

function MainContainer({ step, totalSteps, children }) {
  const offset = (step * 100) / totalSteps;

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white/70 shadow-panel backdrop-blur">
      <div
        className="flex w-[300%] transition-transform duration-500 ease-in-out"
        style={{ transform: `translateX(-${offset}%)` }}
      >
        {Children.map(children, (child, index) => (
          <div key={index} className="w-1/3 shrink-0">
            {child}
          </div>
        ))}
      </div>
    </div>
  );
}

export default MainContainer;
