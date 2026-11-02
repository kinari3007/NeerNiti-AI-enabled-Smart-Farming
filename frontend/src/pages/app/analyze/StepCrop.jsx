import { Field, Input, Select } from '../../../components/ui/Field'
import { GROWTH_STAGES } from '../../../api/crops'
import { useLanguage } from '../../../context/language-context'
import './analyze.css'

/**
 * Step 3 — crop, growth stage, area, and recommendation options.
 * crops: list of CropReference from the backend.
 */
export default function StepCrop({ crop, setCrop, crops, cropsLoading, errors }) {
  const { t } = useLanguage()
  const update = (key) => (e) => setCrop((c) => ({ ...c, [key]: e.target.value }))
  const toggle = (key) => (e) => setCrop((c) => ({ ...c, [key]: e.target.checked }))

  return (
    <div className="step">
      <div className="step__intro">
        <h2 className="step__title">{t('Tell us about your crop')}</h2>
        <p className="step__lead">
          {t('The recommendation is tailored to your crop and its current growth stage.')}
        </p>
      </div>

      <div className="step__grid">
        <Field label={t('Crop')} htmlFor="crop-name" required error={errors.crop_name}>
          <Select
            id="crop-name"
            value={crop.crop_name}
            onChange={update('crop_name')}
            disabled={cropsLoading}
          >
            <option value="">{cropsLoading ? t('Loading crops…') : t('Select a crop')}</option>
            {crops.map((c) => (
              <option key={c.id} value={c.name}>
                {t(c.name)}
              </option>
            ))}
          </Select>
        </Field>

        <Field label={t('Growth stage')} htmlFor="crop-stage" required error={errors.growth_stage}>
          <Select id="crop-stage" value={crop.growth_stage} onChange={update('growth_stage')}>
            <option value="">{t('Select a stage')}</option>
            {GROWTH_STAGES.map((s) => (
              <option key={s} value={s}>
                {t(s)}
              </option>
            ))}
          </Select>
        </Field>

        <Field
          label={t('Cultivated area')}
          htmlFor="crop-area"
          hint={t("Optional. In hectares. Defaults to the farm's area if left blank.")}
          error={errors.area_ha}
        >
          <Input
            id="crop-area"
            type="number"
            step="0.01"
            min="0"
            value={crop.area_ha}
            onChange={update('area_ha')}
            placeholder={t('e.g. 1.0')}
            suffix="ha"
          />
        </Field>
      </div>

      <section className="field-group">
        <h3 className="field-group__title">{t('Options')}</h3>
        <label className="toggle-row">
          <input type="checkbox" checked={crop.use_weather} onChange={toggle('use_weather')} />
          <span>
            <span className="toggle-row__label">{t('Use local weather')}</span>
            <span className="toggle-row__hint">
              {t("Fetch current conditions from your farm's coordinates. Skipped automatically if the farm has no coordinates.")}
            </span>
          </span>
        </label>

        <label className="toggle-row">
          <input
            type="checkbox"
            checked={crop.allow_unverified_prices}
            onChange={toggle('allow_unverified_prices')}
          />
          <span>
            <span className="toggle-row__label">{t('Allow illustrative / unverified prices')}</span>
            <span className="toggle-row__hint">
              {t('The catalogue currently ships sample prices only. Enable this to get a cost-optimized plan — results will clearly mark prices as unverified.')}
            </span>
          </span>
        </label>
      </section>
    </div>
  )
}
