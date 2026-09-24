import { useState } from 'react'
import { Map, Plane, MapPin } from 'lucide-react'

export default function TravelMark() {
  const [paused, setPaused] = useState(false)
  const label = paused ? 'Play travel logo animation' : 'Pause travel logo animation'

  return (
    <button
      type="button"
      className={`brand-symbol travel-mark${paused ? ' travel-mark-paused' : ''}`}
      onClick={() => setPaused((value) => !value)}
      aria-label={label}
      title={label}
    >
      <Map className="travel-mark-stage travel-mark-plan" aria-hidden="true" />
      <Plane className="travel-mark-stage travel-mark-flight" aria-hidden="true" />
      <MapPin className="travel-mark-stage travel-mark-arrival" aria-hidden="true" />
    </button>
  )
}
