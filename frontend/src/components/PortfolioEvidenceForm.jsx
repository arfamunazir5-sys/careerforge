import "./Phase3.css";

function PortfolioEvidenceForm({ value, onChange, linksError, casesError }) {
  const set = (patch) => onChange({ ...value, ...patch });

  return (
    <div className="pf-field">
      <label className="pf-label" htmlFor="pf-links">
        Portfolio links <span className="pf-optional">(one per line, up to 5, optional)</span>
      </label>
      <textarea
        id="pf-links"
        rows="4"
        className={`pf-input ${linksError ? "invalid" : ""}`}
        value={value.links}
        onChange={(e) => set({ links: e.target.value })}
        placeholder={"behance.net/yourname\nyourname.design/case-study"}
      />
      {linksError ? (
        <span className="pf-error">{linksError}</span>
      ) : (
        <span className="pf-help">
          Case studies, a portfolio site or published work. Links are checked for format and platform, and
          never opened.
        </span>
      )}

      <label className="pf-label" htmlFor="pf-cases" style={{ marginTop: 12 }}>
        Finished case studies or projects you can show
      </label>
      <input
        id="pf-cases"
        type="number"
        min="0"
        max="20"
        className={`pf-input ${casesError ? "invalid" : ""}`}
        value={value.caseStudies}
        onChange={(e) => set({ caseStudies: e.target.value })}
      />
      {casesError && <span className="pf-error">{casesError}</span>}

      <label className={`as-option ${value.hasResults ? "selected" : ""}`}>
        <input type="checkbox" checked={value.hasResults} onChange={(e) => set({ hasResults: e.target.checked })} />
        <span>My work shows measurable results (numbers or outcomes)</span>
      </label>
      <label className={`as-option ${value.hasProcess ? "selected" : ""}`}>
        <input type="checkbox" checked={value.hasProcess} onChange={(e) => set({ hasProcess: e.target.checked })} />
        <span>My work explains the problem, my approach and the outcome</span>
      </label>
      <label className={`as-option ${value.recentWork ? "selected" : ""}`}>
        <input type="checkbox" checked={value.recentWork} onChange={(e) => set({ recentWork: e.target.checked })} />
        <span>I added something in the last 6 months</span>
      </label>
      <span className="pf-help">This is self-reported evidence, so be honest: it sets how much time the Portfolio agent asks for.</span>
    </div>
  );
}

export default PortfolioEvidenceForm;