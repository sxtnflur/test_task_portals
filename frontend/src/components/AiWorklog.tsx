import { useEffect, useState } from 'react'
import { marked } from 'marked'

export function AiWorklog() {
  const [html, setHtml] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    // A plain static file (served from `public/`), not bundled into the JS -
    // fetched with the app's own base URL so it still resolves when the
    // build is served from a subfolder or opened via `file://`.
    fetch(`${import.meta.env.BASE_URL}ai-worklog.md`)
      .then((res) => (res.ok ? res.text() : Promise.reject(new Error(String(res.status)))))
      .then((markdown) => {
        if (cancelled) return
        // Our own static file, never user input - safe to render as-is.
        setHtml(marked.parse(markdown, { async: false }))
      })
      .catch(() => {
        if (!cancelled) setHtml(null)
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (!html) {
    return null
  }

  return (
    <footer className="ai-worklog">
      <div className="ai-worklog-inner">
        {/* eslint-disable-next-line react/no-danger */}
        <div className="ai-worklog-content" dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    </footer>
  )
}
