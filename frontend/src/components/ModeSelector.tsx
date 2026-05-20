import type { SourceType } from '../types'

interface ModeSelectorProps {
  value: SourceType
  options: SourceType[]
  onChange: (mode: SourceType) => void
}

export function ModeSelector({ value, options, onChange }: ModeSelectorProps) {
  return (
    <div className="mode-selector">
      {options.map(mode => (
        <button
          key={mode}
          type="button"
          className={mode === value ? 'mode-chip active' : 'mode-chip'}
          onClick={() => onChange(mode)}
        >
          {mode}
        </button>
      ))}
    </div>
  )
}
