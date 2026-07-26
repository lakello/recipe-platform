export async function reportWebVitals() {
  const { onCLS, onINP, onLCP } = await import('web-vitals')
  const report = (metric: { name: string; value: number }) =>
    console.info(`[Web Vitals] ${metric.name}:`, metric.value)

  const options = { reportAllChanges: true }
  onCLS(report, options)
  onINP(report, options)
  onLCP(report, options)
}
