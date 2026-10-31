import { Field, Input, Select } from '../../../components/ui/Field'
import { AREA_UNITS } from '../../../api/farms'
import { useFarm } from '../../../context/farm-context'
import './analyze.css'

/**
 * Step 1 — choose an existing farm or create a new one.
 * mode: 'existing' | 'new'
 */
export default function StepFarm({ mode, setMode, newFarm, setNewFarm, errors }) {
  const { farms, activeFarmId, setActiveFarmId, hasFarms } = useFarm()

  const update = (key) => (e) => setNewFarm((f) => ({ ...f, [key]: e.target.value }))

  return (
    <div className="step">
      <div className="step__intro">
        <h2 className="step__title">Which farm are we analyzing?</h2>
        <p className="step__lead">
          Pick an existing farm or add a new one. Coordinates are optional but let us
          fetch local weather for your analysis.
        </p>
      </div>

      {hasFarms && (
        <div className="farm-mode">
          <button
            type="button"
            className={`farm-mode__btn ${mode === 'existing' ? 'farm-mode__btn--active' : ''}`}
            onClick={() => setMode('existing')}
          >
            Use an existing farm
          </button>
          <button
            type="button"
            className={`farm-mode__btn ${mode === 'new' ? 'farm-mode__btn--active' : ''}`}
            onClick={() => setMode('new')}
          >
            Add a new farm
          </button>
        </div>
      )}

      {mode === 'existing' && hasFarms ? (
        <Field label="Select farm" htmlFor="farm-select">
          <Select
            id="farm-select"
            value={activeFarmId}
            onChange={(e) => setActiveFarmId(e.target.value)}
          >
            {farms.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
                {f.location_description ? ` — ${f.location_description}` : ''}
              </option>
            ))}
          </Select>
        </Field>
      ) : (
        <div className="step__grid">
          <Field
            label="Farm name"
            htmlFor="farm-name"
            required
            error={errors.name}
            className="step__grid-full"
          >
            <Input
              id="farm-name"
              value={newFarm.name}
              onChange={update('name')}
              placeholder="e.g. Green Valley Farm"
              maxLength={255}
            />
          </Field>

          <Field
            label="Area"
            htmlFor="farm-area"
            hint="Optional. Used to scale total fertilizer quantities."
            error={errors.area_value}
          >
            <Input
              id="farm-area"
              type="number"
              min="0"
              step="0.01"
              value={newFarm.area_value}
              onChange={update('area_value')}
              placeholder="e.g. 2.5"
            />
          </Field>

          <Field label="Area unit" htmlFor="farm-area-unit">
            <Select id="farm-area-unit" value={newFarm.area_unit} onChange={update('area_unit')}>
              {AREA_UNITS.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </Select>
          </Field>

          <Field
            label="Latitude"
            htmlFor="farm-lat"
            hint="Optional — provide with longitude for weather."
            error={errors.latitude}
          >
            <Input
              id="farm-lat"
              type="number"
              step="0.0001"
              value={newFarm.latitude}
              onChange={update('latitude')}
              placeholder="e.g. 28.6139"
            />
          </Field>

          <Field label="Longitude" htmlFor="farm-lon" error={errors.longitude}>
            <Input
              id="farm-lon"
              type="number"
              step="0.0001"
              value={newFarm.longitude}
              onChange={update('longitude')}
              placeholder="e.g. 77.2090"
            />
          </Field>

          <Field
            label="Location description"
            htmlFor="farm-loc"
            hint="Optional."
            className="step__grid-full"
          >
            <Input
              id="farm-loc"
              value={newFarm.location_description}
              onChange={update('location_description')}
              placeholder="e.g. Village Rampur, District Agra"
              maxLength={500}
            />
          </Field>
        </div>
      )}
    </div>
  )
}
