import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../../../components/ui/Card'
import Button from '../../../components/ui/Button'
import { Spinner } from '../../../components/ui/Feedback'
import PageHeader from '../../../components/app/PageHeader'
import Stepper from '../../../components/app/Stepper'
import StepFarm from './StepFarm'
import StepSoil from './StepSoil'
import StepCrop from './StepCrop'
import { useFarm } from '../../../context/farm-context'
import { useToast } from '../../../components/ui/ToastProvider'
import { farmsApi } from '../../../api/farms'
import { soilApi } from '../../../api/soil'
import { cropsApi } from '../../../api/crops'
import { recommendationsApi } from '../../../api/recommendations'
import { IconArrow } from '../../../assets/illustrations/decor'
import './analyze.css'

const STEPS = [{ label: 'Farm' }, { label: 'Soil' }, { label: 'Crop & Options' }]

const EMPTY_FARM = {
  name: '',
  area_value: '',
  area_unit: 'hectare',
  latitude: '',
  longitude: '',
  location_description: '',
}

const EMPTY_SOIL = {
  soil_ph: '',
  soil_moisture: '',
  moisture_unit: '',
  electrical_conductivity: '',
  ec_unit: '',
  organic_carbon: '',
  organic_carbon_unit: '',
  nitrogen: '',
  phosphorus: '',
  potassium: '',
  npk_unit: '',
}

const EMPTY_CROP = {
  crop_name: '',
  growth_stage: '',
  area_ha: '',
  use_weather: true,
  allow_unverified_prices: true,
}

const num = (v) => (v === '' || v == null ? null : Number(v))

export default function AnalyzePage() {
  const navigate = useNavigate()
  const toast = useToast()
  const { hasFarms, activeFarmId, setActiveFarmId, reloadFarms } = useFarm()

  const [step, setStep] = useState(0)
  const [mode, setMode] = useState('existing') // existing | new
  const [newFarm, setNewFarm] = useState(EMPTY_FARM)
  const [soil, setSoil] = useState(EMPTY_SOIL)
  const [crop, setCrop] = useState(EMPTY_CROP)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const [crops, setCrops] = useState([])
  const [cropsLoading, setCropsLoading] = useState(true)

  // Default to "new farm" mode when the farmer has no farms yet.
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (!hasFarms) setMode('new')
  }, [hasFarms])
  /* eslint-enable react-hooks/set-state-in-effect */

  useEffect(() => {
    cropsApi
      .list()
      .then((data) => setCrops(data || []))
      .catch(() => toast.error('Could not load the crop list.'))
      .finally(() => setCropsLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  /* ---------------- validation ---------------- */

  function validateFarmStep() {
    const e = {}
    if (mode === 'new') {
      if (!newFarm.name.trim()) e.name = 'Please enter a farm name.'
      if (newFarm.area_value !== '' && Number(newFarm.area_value) <= 0)
        e.area_value = 'Area must be greater than 0.'
      const latSet = newFarm.latitude !== ''
      const lonSet = newFarm.longitude !== ''
      if (latSet !== lonSet) {
        const msg = 'Provide latitude and longitude together, or neither.'
        if (!latSet) e.latitude = msg
        if (!lonSet) e.longitude = msg
      }
      if (latSet && (Number(newFarm.latitude) < -90 || Number(newFarm.latitude) > 90))
        e.latitude = 'Latitude must be between -90 and 90.'
      if (lonSet && (Number(newFarm.longitude) < -180 || Number(newFarm.longitude) > 180))
        e.longitude = 'Longitude must be between -180 and 180.'
    } else if (!activeFarmId) {
      e.name = 'Please select a farm.'
    }
    setErrors(e)
    return Object.keys(e).length === 0
  }

  function validateSoilStep() {
    const e = {}
    const rangeCheck = (key, min, max, label) => {
      if (soil[key] !== '') {
        const v = Number(soil[key])
        if (Number.isNaN(v)) e[key] = `${label} must be a number.`
        else if (v < min || v > max) e[key] = `${label} must be between ${min} and ${max}.`
      }
    }
    rangeCheck('soil_ph', 0, 14, 'pH')
    rangeCheck('soil_moisture', 0, 100, 'Moisture')
    rangeCheck('electrical_conductivity', 0, 20, 'EC')
    rangeCheck('organic_carbon', 0, 100, 'Organic carbon')
    rangeCheck('nitrogen', 0, 10000, 'Nitrogen')
    rangeCheck('phosphorus', 0, 10000, 'Phosphorus')
    rangeCheck('potassium', 0, 10000, 'Potassium')

    // Unit-required-when-value rules (mirror backend)
    if (soil.soil_moisture !== '' && !soil.moisture_unit)
      e.moisture_unit = 'Select a moisture unit.'
    if (soil.electrical_conductivity !== '' && !soil.ec_unit)
      e.ec_unit = 'Select an EC unit.'
    if (soil.organic_carbon !== '' && !soil.organic_carbon_unit)
      e.organic_carbon_unit = 'Select an organic carbon unit.'
    const npkEntered = soil.nitrogen !== '' || soil.phosphorus !== '' || soil.potassium !== ''
    if (npkEntered && !soil.npk_unit) e.npk_unit = 'Select an N–P–K unit.'

    setErrors(e)
    return Object.keys(e).length === 0
  }

  function validateCropStep() {
    const e = {}
    if (!crop.crop_name) e.crop_name = 'Please select a crop.'
    if (!crop.growth_stage) e.growth_stage = 'Please select a growth stage.'
    if (crop.area_ha !== '' && Number(crop.area_ha) <= 0)
      e.area_ha = 'Area must be greater than 0.'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  /* ---------------- navigation ---------------- */

  function next() {
    if (step === 0 && !validateFarmStep()) return
    if (step === 1 && !validateSoilStep()) return
    setErrors({})
    setStep((s) => Math.min(s + 1, STEPS.length - 1))
  }

  function back() {
    setErrors({})
    setStep((s) => Math.max(s - 1, 0))
  }

  /* ---------------- submit ---------------- */

  function soilHasAnyValue() {
    return [
      'soil_ph', 'soil_moisture', 'electrical_conductivity', 'organic_carbon',
      'nitrogen', 'phosphorus', 'potassium',
    ].some((k) => soil[k] !== '')
  }

  async function handleSubmit() {
    if (!validateCropStep()) return
    setSubmitting(true)
    try {
      // 1. Resolve farm (create if needed)
      let farmId = activeFarmId
      if (mode === 'new') {
        const payload = {
          name: newFarm.name.trim(),
          area_value: num(newFarm.area_value),
          area_unit: newFarm.area_value !== '' ? newFarm.area_unit : null,
          latitude: num(newFarm.latitude),
          longitude: num(newFarm.longitude),
          location_description: newFarm.location_description.trim() || null,
        }
        const created = await farmsApi.create(payload)
        farmId = created.id
        await reloadFarms()
        setActiveFarmId(farmId)
        toast.success(`Farm "${created.name}" created.`)
      }

      // 2. Submit a soil reading (only if the farmer entered any measurement)
      if (soilHasAnyValue()) {
        const reading = {
          collected_at: new Date().toISOString(),
          data_source: 'manual',
          soil_ph: num(soil.soil_ph),
          soil_moisture: num(soil.soil_moisture),
          moisture_unit: soil.moisture_unit || null,
          electrical_conductivity: num(soil.electrical_conductivity),
          ec_unit: soil.ec_unit || null,
          organic_carbon: num(soil.organic_carbon),
          organic_carbon_unit: soil.organic_carbon_unit || null,
          nitrogen: num(soil.nitrogen),
          phosphorus: num(soil.phosphorus),
          potassium: num(soil.potassium),
          npk_unit: soil.npk_unit || null,
        }
        await soilApi.createReading(farmId, reading)
      }

      // 3. Generate the recommendation
      const recPayload = {
        crop_name: crop.crop_name,
        growth_stage: crop.growth_stage,
        area_ha: num(crop.area_ha),
        use_weather: crop.use_weather,
        allow_unverified_prices: crop.allow_unverified_prices,
      }
      const rec = await recommendationsApi.create(farmId, recPayload)

      toast.success('Recommendation generated.')
      navigate(`/app/recommendations/${rec.id}`)
    } catch (err) {
      toast.error(err.message || 'Something went wrong. Please try again.')
      setSubmitting(false)
    }
  }

  return (
    <div className="wizard">
      <PageHeader
        eyebrow="Analyze Soil"
        title="Generate a fertilizer recommendation"
        subtitle="Three quick steps: choose your farm, enter any soil measurements you have, and pick your crop."
      />

      <Card tone="surface" className="wizard__card">
        <Stepper steps={STEPS} current={step} />

        {step === 0 && (
          <StepFarm
            mode={mode}
            setMode={setMode}
            newFarm={newFarm}
            setNewFarm={setNewFarm}
            errors={errors}
          />
        )}
        {step === 1 && <StepSoil soil={soil} setSoil={setSoil} errors={errors} />}
        {step === 2 && (
          <StepCrop
            crop={crop}
            setCrop={setCrop}
            crops={crops}
            cropsLoading={cropsLoading}
            errors={errors}
          />
        )}

        <div className="wizard__footer">
          {step > 0 ? (
            <Button variant="ghost" onClick={back} disabled={submitting}>
              Back
            </Button>
          ) : (
            <span />
          )}

          <div className="wizard__footer-right">
            {step < STEPS.length - 1 ? (
              <Button variant="primary" onClick={next} iconRight={<IconArrow />}>
                Continue
              </Button>
            ) : (
              <Button variant="gold" onClick={handleSubmit} disabled={submitting}>
                {submitting ? (
                  <>
                    <Spinner size={16} /> Generating…
                  </>
                ) : (
                  'Get Recommendation'
                )}
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
}
