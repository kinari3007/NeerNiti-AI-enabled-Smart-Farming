import { useFarm } from '../../context/farm-context'
import { Select } from '../ui/Field'
import { IconSoil } from '../../assets/illustrations/decor'
import { useLanguage } from '../../context/language-context'
import './FarmSwitcher.css'

/**
 * FarmSwitcher — lets the farmer pick which farm is active.
 * Hidden when there are no farms (the page handles the empty state).
 */
export default function FarmSwitcher() {
  const { farms, activeFarmId, setActiveFarmId } = useFarm()
  const { t } = useLanguage()

  if (!farms.length) return null

  return (
    <div className="farm-switcher">
      <span className="farm-switcher__icon" aria-hidden="true">
        <IconSoil size={18} />
      </span>
      <label className="sr-only" htmlFor="farm-switcher-select">
        {t('Active farm')}
      </label>
      <Select
        id="farm-switcher-select"
        value={activeFarmId}
        onChange={(e) => setActiveFarmId(e.target.value)}
        className="farm-switcher__select"
      >
        {farms.map((f) => (
          <option key={f.id} value={f.id}>
            {f.name}
          </option>
        ))}
      </Select>
    </div>
  )
}
