/**
 * Section heading with an optional leading icon (a lucide-react
 * component, passed as `Icon`) — used for Flights/Hotels/Recommendations/
 * Warnings/Trip Summary so each section reads at a glance.
 */
export default function SectionTitle({ icon: Icon, meta, children }) {
  return (
    <h2 className="section-title text-ink mb-3 flex items-center gap-2 text-sm font-semibold">
      {Icon && <Icon className="h-3.5 w-3.5" aria-hidden="true" />}
      <span>{children}</span>
      {meta && <span className="section-title-meta">{meta}</span>}
    </h2>
  )
}
