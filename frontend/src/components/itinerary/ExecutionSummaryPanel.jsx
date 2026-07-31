import { useState } from 'react'
import StatItem from '../common/StatItem'

/**
 * Optional, collapsed-by-default developer section surfacing the
 * backend's execution/validation/fallback summaries verbatim — useful
 * for debugging, not meant to be primary content for an end user.
 */
export default function ExecutionSummaryPanel({
  executionSummary,
  toolResultsSummary,
  validationSummary,
  fallbackSummary,
}) {
  const [expanded, setExpanded] = useState(false)
  const hasData = Boolean(executionSummary) || (toolResultsSummary && toolResultsSummary.length > 0)
  if (!hasData) return null

  return (
    <section className="border-border bg-surface rounded-xl border">
      <button
        type="button"
        onClick={() => setExpanded((prev) => !prev)}
        className="text-ink-muted hover:text-ink flex w-full items-center justify-between px-4 py-3 text-left text-xs font-bold tracking-wide uppercase transition"
      >
        <span>Execution Summary</span>
        <span className="text-ink-muted">{expanded ? 'Hide' : 'Show'}</span>
      </button>

      {expanded && (
        <div className="animate-fade-in border-border text-ink-muted space-y-3 border-t px-4 py-3 text-xs">
          {executionSummary && (
            <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <StatItem label="Tools run" value={executionSummary.total_tools} />
              <StatItem label="Succeeded" value={executionSummary.successful_tools} />
              <StatItem label="Failed" value={executionSummary.failed_tools} />
              <StatItem label="Time (ms)" value={executionSummary.total_execution_time_ms} />
            </dl>
          )}

          {toolResultsSummary?.length > 0 && (
            <ul className="space-y-1">
              {toolResultsSummary.map((tool) => (
                <li key={tool.tool_name} className="flex justify-between gap-2">
                  <span>{tool.display_name}</span>
                  <span className="text-ink-muted">
                    {tool.status} - {tool.items_found} found{tool.recovered ? ' - recovered' : ''}
                  </span>
                </li>
              ))}
            </ul>
          )}

          {validationSummary && (
            <p>
              Validation: {validationSummary.overall_status} ({validationSummary.issues_count} issue(s),{' '}
              {validationSummary.warnings_count} warning(s))
            </p>
          )}

          {fallbackSummary?.fallback_triggered && (
            <p>
              Fallback: {fallbackSummary.total_retry_attempts} retry attempt(s),{' '}
              {fallbackSummary.tools_recovered.length} recovered
            </p>
          )}
        </div>
      )}
    </section>
  )
}
