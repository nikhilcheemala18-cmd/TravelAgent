/**
 * Section heading with an optional leading icon (a lucide-react
 * component, passed as `Icon`) — used for Flights/Hotels/Recommendations/
 * Warnings/Trip Summary so each section reads at a glance.
 */
export default function SectionTitle({ icon: Icon, children }) {
  return (
    <h2 className="text-ink-muted mb-2 flex items-center gap-1.5 text-xs font-bold tracking-wide uppercase">
      {Icon && <Icon className="h-3.5 w-3.5" aria-hidden="true" />}
      {children}
    </h2>
  )
}
