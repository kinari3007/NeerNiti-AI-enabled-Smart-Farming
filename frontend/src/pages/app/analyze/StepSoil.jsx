import { Field, Input, Select } from '../../../components/ui/Field'
import { EC_UNITS, MOISTURE_UNITS, NPK_UNITS, OC_UNITS } from '../../../api/soil'
import { useLanguage } from '../../../context/language-context'
import './analyze.css'

/**
 * Step 2 — soil measurements.
 *
 * Only fields the backend SoilReadingCreate schema accepts are shown.
 * Every field is optional (sensors don't measure everything), but a unit is
 * required whenever a value is entered — mirroring the backend validation.
 */
export default function StepSoil({ soil, setSoil, errors }) {
  const { t } = useLanguage()
  const update = (key) => (e) => setSoil((s) => ({ ...s, [key]: e.target.value }))

  return (
    <div className="step">
      <div className="step__intro">
        <h2 className="step__title">{t('Enter your soil measurements')}</h2>
        <p className="step__lead">
          {t('Add whatever you have — a lab report or sensor reading. Every field is optional, but please include the unit for any value you enter.')}
        </p>
      </div>

      {/* --- Soil properties --- */}
      <section className="field-group">
        <h3 className="field-group__title">{t('Soil properties')}</h3>
        <div className="step__grid">
          <Field
            label={t('Soil pH')}
            htmlFor="soil-ph"
            hint={t('0–14. Typical agronomic range is 4.0–8.5.')}
            error={errors.soil_ph}
          >
            <Input
              id="soil-ph"
              type="number"
              step="0.1"
              min="0"
              max="14"
              value={soil.soil_ph}
              onChange={update('soil_ph')}
              placeholder="e.g. 6.8"
            />
          </Field>

          <div className="paired-field">
            <Field label={t('Moisture')} htmlFor="soil-moisture" error={errors.soil_moisture}>
              <Input
                id="soil-moisture"
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={soil.soil_moisture}
                onChange={update('soil_moisture')}
                placeholder="e.g. 35"
              />
            </Field>
            <Field label={t('Unit')} htmlFor="soil-moisture-unit" error={errors.moisture_unit}>
              <Select id="soil-moisture-unit" value={soil.moisture_unit} onChange={update('moisture_unit')}>
                <option value="">—</option>
                {MOISTURE_UNITS.map((u) => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </Select>
            </Field>
          </div>

          <div className="paired-field">
            <Field label={t('Electrical conductivity')} htmlFor="soil-ec" error={errors.electrical_conductivity}>
              <Input
                id="soil-ec"
                type="number"
                step="0.01"
                min="0"
                max="20"
                value={soil.electrical_conductivity}
                onChange={update('electrical_conductivity')}
                placeholder="e.g. 1.2"
              />
            </Field>
            <Field label={t('Unit')} htmlFor="soil-ec-unit" error={errors.ec_unit}>
              <Select id="soil-ec-unit" value={soil.ec_unit} onChange={update('ec_unit')}>
                <option value="">—</option>
                {EC_UNITS.map((u) => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </Select>
            </Field>
          </div>

          <div className="paired-field">
            <Field label={t('Organic carbon')} htmlFor="soil-oc" error={errors.organic_carbon}>
              <Input
                id="soil-oc"
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={soil.organic_carbon}
                onChange={update('organic_carbon')}
                placeholder="e.g. 0.6"
              />
            </Field>
            <Field label={t('Unit')} htmlFor="soil-oc-unit" error={errors.organic_carbon_unit}>
              <Select id="soil-oc-unit" value={soil.organic_carbon_unit} onChange={update('organic_carbon_unit')}>
                <option value="">—</option>
                {OC_UNITS.map((u) => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </Select>
            </Field>
          </div>
        </div>
      </section>

      {/* --- Nutrients --- */}
      <section className="field-group">
        <h3 className="field-group__title">{t('Nutrients (N–P–K)')}</h3>
        <p className="field-group__note">
          {t('Nitrogen, phosphorus, and potassium must share a single unit.')}
        </p>
        <div className="step__grid">
          <Field label={t('Nitrogen (N)')} htmlFor="soil-n" error={errors.nitrogen}>
            <Input
              id="soil-n"
              type="number"
              step="0.1"
              min="0"
              value={soil.nitrogen}
              onChange={update('nitrogen')}
              placeholder="e.g. 80"
            />
          </Field>
          <Field label={t('Phosphorus (P)')} htmlFor="soil-p" error={errors.phosphorus}>
            <Input
              id="soil-p"
              type="number"
              step="0.1"
              min="0"
              value={soil.phosphorus}
              onChange={update('phosphorus')}
              placeholder="e.g. 40"
            />
          </Field>
          <Field label={t('Potassium (K)')} htmlFor="soil-k" error={errors.potassium}>
            <Input
              id="soil-k"
              type="number"
              step="0.1"
              min="0"
              value={soil.potassium}
              onChange={update('potassium')}
              placeholder="e.g. 200"
            />
          </Field>
          <Field label={t('N–P–K unit')} htmlFor="soil-npk-unit" error={errors.npk_unit}>
            <Select id="soil-npk-unit" value={soil.npk_unit} onChange={update('npk_unit')}>
              <option value="">—</option>
              {NPK_UNITS.map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </Select>
          </Field>
        </div>
      </section>

      <p className="step__hint-block">
        {t("Temperature, humidity, and rainfall are fetched automatically from a weather service using your farm's coordinates — you don't need to enter them here.")}
      </p>
    </div>
  )
}
