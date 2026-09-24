import { useLayoutEffect, useState } from 'react'

const STORAGE_KEY = 'flyo-theme'

export function useTheme() {
  const [theme, setTheme] = useState(() => {
    try {
      return window.localStorage.getItem(STORAGE_KEY) === 'dark' ? 'dark' : 'light'
    } catch {
      return 'light'
    }
  })

  useLayoutEffect(() => {
    document.documentElement.dataset.theme = theme
    try {
      window.localStorage.setItem(STORAGE_KEY, theme)
    } catch {
      // The toggle still works when browser storage is unavailable.
    }
  }, [theme])

  return { theme, setTheme }
}
