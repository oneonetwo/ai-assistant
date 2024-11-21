interface PerformanceMetrics {
  fcp: number // First Contentful Paint
  lcp: number // Largest Contentful Paint
  fid: number // First Input Delay
  cls: number // Cumulative Layout Shift
}

export function initializePerformanceMonitoring() {
  // 监听 FCP
  new PerformanceObserver((entryList) => {
    const entries = entryList.getEntries()
    if (entries.length > 0) {
      const fcp = entries[0].startTime
      reportMetric('fcp', fcp)
    }
  }).observe({ entryTypes: ['paint'] })

  // 监听 LCP
  new PerformanceObserver((entryList) => {
    const entries = entryList.getEntries()
    if (entries.length > 0) {
      const lcp = entries[entries.length - 1].startTime
      reportMetric('lcp', lcp)
    }
  }).observe({ entryTypes: ['largest-contentful-paint'] })

  // 监听 FID
  new PerformanceObserver((entryList) => {
    const entries = entryList.getEntries()
    entries.forEach((entry) => {
      if (entry.processingStart && entry.startTime) {
        const fid = entry.processingStart - entry.startTime
        reportMetric('fid', fid)
      }
    })
  }).observe({ entryTypes: ['first-input'] })

  // 监听 CLS
  let clsValue = 0
  new PerformanceObserver((entryList) => {
    const entries = entryList.getEntries()
    entries.forEach((entry) => {
      if (!entry.hadRecentInput) {
        clsValue += entry.value
        reportMetric('cls', clsValue)
      }
    })
  }).observe({ entryTypes: ['layout-shift'] })
}

function reportMetric(name: keyof PerformanceMetrics, value: number) {
  // 可以将指标发送到分析服务
  console.log(`Performance metric - ${name}:`, value)
} 