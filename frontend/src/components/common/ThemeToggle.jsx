import { Moon, Sun } from 'lucide-react'

export default function ThemeToggle({ theme, onThemeChange }) {
  return (
    <div className="theme-toggle" role="group" aria-label="Appearance">
      <button
        type="button"
        aria-label="Light theme"
        title="Light theme"
        aria-pressed={theme === 'light'}
        onClick={() => onThemeChange('light')}
      >
        <Sun aria-hidden="true" />
      </button>
      <button
        type="button"
        aria-label="Dark theme"
        title="Dark theme"
        aria-pressed={theme === 'dark'}
        onClick={() => onThemeChange('dark')}
      >
        <Moon aria-hidden="true" />
      </button>
    </div>
  )
}
