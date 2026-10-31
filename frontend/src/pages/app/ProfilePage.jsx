import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import { Field, Input, Select } from '../../components/ui/Field'
import { Spinner } from '../../components/ui/Feedback'
import { EmptyState } from '../../components/ui/States'
import { ConfirmDialog } from '../../components/ui/Modal'
import PageHeader from '../../components/app/PageHeader'
import FarmSwitcher from '../../components/app/FarmSwitcher'
import { useFarm } from '../../context/farm-context'
import { useToast } from '../../components/ui/ToastProvider'
import { session } from '../../api/session'
import { farmsApi, AREA_UNITS } from '../../api/farms'
import { formatDateTime } from '../../utils/format'
import { LeafMark, IconArrow, IconProfile } from '../../assets/illustrations/decor'
import './ProfilePage.css'

export default function ProfilePage() {
  const navigate = useNavigate()
  const toast = useToast()
  const { activeFarm, hasFarms, loading: farmsLoading, reloadFarms, setActiveFarmId } = useFarm()

  const [name, setName] = useState(session.getName())
  const [savingName, setSavingName] = useState(false)

  const [farmForm, setFarmForm] = useState(null)
  const [savingFarm, setSavingFarm] = useState(false)
  const [farmErrors, setFarmErrors] = useState({})
  const [logoutOpen, setLogoutOpen] = useState(false)

  // Sync farm form when the active farm changes
  // Sync the editable form when the active farm changes.
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (activeFarm) {
      setFarmForm({
        name: activeFarm.name || '',
        area_value: activeFarm.area_value ?? '',
        area_unit: activeFarm.area_unit || 'hectare',
        latitude: activeFarm.latitude ?? '',
        longitude: activeFarm.longitude ?? '',
        location_description: activeFarm.location_description || '',
        irrigation_water_ph: activeFarm.irrigation_water_ph ?? '',
        irrigation_water_ph_source: activeFarm.irrigation_water_ph_source || '',
      })
      setFarmErrors({})
    }
  }, [activeFarm])
  /* eslint-enable react-hooks/set-state-in-effect */

  const num = (v) => (v === '' || v == null ? null : Number(v))

  function saveName() {
    setSavingName(true)
    session.setName(name.trim())
    setTimeout(() => {
      setSavingName(false)
      toast.success('Your name has been saved.')
    }, 150)
  }

  function validateFarm() {
    const e = {}
    if (!farmForm.name.trim()) e.name = 'Farm name is required.'
    const latSet = farmForm.latitude !== '' && farmForm.latitude != null
    const lonSet = farmForm.longitude !== '' && farmForm.longitude != null
    if (latSet !== lonSet) {
      const msg = 'Provide latitude and longitude together, or neither.'
      if (!latSet) e.latitude = msg
      if (!lonSet) e.longitude = msg
    }
    if (farmForm.irrigation_water_ph !== '' && farmForm.irrigation_water_ph != null) {
      const ph = Number(farmForm.irrigation_water_ph)
      if (ph < 0 || ph > 14) e.irrigation_water_ph = 'pH must be between 0 and 14.'
    }
    setFarmErrors(e)
    return Object.keys(e).length === 0
  }

  async function saveFarm() {
    if (!validateFarm()) return
    setSavingFarm(true)
    try {
      const payload = {
        name: farmForm.name.trim(),
        area_value: num(farmForm.area_value),
        area_unit: farmForm.area_value !== '' ? farmForm.area_unit : null,
        latitude: num(farmForm.latitude),
        longitude: num(farmForm.longitude),
        location_description: farmForm.location_description.trim() || null,
        irrigation_water_ph: num(farmForm.irrigation_water_ph),
        irrigation_water_ph_source: farmForm.irrigation_water_ph_source.trim() || null,
      }
      await farmsApi.update(activeFarm.id, payload)
      await reloadFarms()
      toast.success('Farm details updated.')
    } catch (err) {
      toast.error(err.message || 'Could not update the farm.')
    } finally {
      setSavingFarm(false)
    }
  }

  function handleLogout() {
    session.clear()
    setActiveFarmId('')
    setLogoutOpen(false)
    toast.info('Signed out on this device.')
    navigate('/')
  }

  const update = (key) => (e) => setFarmForm((f) => ({ ...f, [key]: e.target.value }))

  return (
    <>
      <PageHeader
        eyebrow="Profile"
        title="Your profile & farm"
        subtitle="Manage your display name and the details of your selected farm."
        actions={hasFarms ? <FarmSwitcher /> : null}
      />

      {/* Account note — honest about no server-side auth */}
      <Card tone="sage" className="profile-note">
        <IconProfile size={22} />
        <p>
          This app currently runs without server-side accounts. Your name and selected
          farm are stored only on this device. Farm records themselves are saved on the
          server.
        </p>
      </Card>

      <div className="profile-grid">
        {/* Farmer info */}
        <Card tone="surface" className="profile-card">
          <h2 className="profile-card__title">Farmer details</h2>
          <Field
            label="Display name"
            htmlFor="profile-name"
            hint="Used to greet you across the app."
          >
            <Input
              id="profile-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Ramesh Kumar"
              maxLength={80}
            />
          </Field>
          <div className="profile-card__actions">
            <Button variant="primary" onClick={saveName} disabled={savingName}>
              {savingName ? 'Saving…' : 'Save name'}
            </Button>
          </div>
        </Card>

        {/* Farm details */}
        <Card tone="surface" className="profile-card profile-card--wide">
          <h2 className="profile-card__title">Farm details</h2>

          {farmsLoading && (
            <div className="profile-loading">
              <Spinner /> <span>Loading your farm…</span>
            </div>
          )}

          {!farmsLoading && !hasFarms && (
            <EmptyState
              illustration={<LeafMark size={40} />}
              title="No farm yet"
              message="Add your first farm through the soil analysis flow."
              action={
                <Button as="link" to="/app/analyze" variant="primary" iconRight={<IconArrow />}>
                  Analyze My Soil
                </Button>
              }
            />
          )}

          {!farmsLoading && hasFarms && farmForm && (
            <>
              <div className="profile-form-grid">
                <Field label="Farm name" htmlFor="pf-name" required error={farmErrors.name} className="profile-full">
                  <Input id="pf-name" value={farmForm.name} onChange={update('name')} maxLength={255} />
                </Field>

                <Field label="Area" htmlFor="pf-area">
                  <Input
                    id="pf-area"
                    type="number"
                    min="0"
                    step="0.01"
                    value={farmForm.area_value}
                    onChange={update('area_value')}
                    placeholder="e.g. 2.5"
                  />
                </Field>
                <Field label="Area unit" htmlFor="pf-area-unit">
                  <Select id="pf-area-unit" value={farmForm.area_unit} onChange={update('area_unit')}>
                    {AREA_UNITS.map((u) => (
                      <option key={u} value={u}>{u}</option>
                    ))}
                  </Select>
                </Field>

                <Field label="Latitude" htmlFor="pf-lat" error={farmErrors.latitude}>
                  <Input
                    id="pf-lat"
                    type="number"
                    step="0.0001"
                    value={farmForm.latitude}
                    onChange={update('latitude')}
                    placeholder="e.g. 28.6139"
                  />
                </Field>
                <Field label="Longitude" htmlFor="pf-lon" error={farmErrors.longitude}>
                  <Input
                    id="pf-lon"
                    type="number"
                    step="0.0001"
                    value={farmForm.longitude}
                    onChange={update('longitude')}
                    placeholder="e.g. 77.2090"
                  />
                </Field>

                <Field label="Location" htmlFor="pf-loc" className="profile-full">
                  <Input
                    id="pf-loc"
                    value={farmForm.location_description}
                    onChange={update('location_description')}
                    placeholder="Village, district, state"
                    maxLength={500}
                  />
                </Field>
              </div>

              <div className="profile-subsection">
                <h3 className="profile-subsection__title">Irrigation water</h3>
                <div className="profile-form-grid">
                  <Field
                    label="Irrigation water pH"
                    htmlFor="pf-iph"
                    hint="Optional. 0–14. Surfaced as advisory context in recommendations."
                    error={farmErrors.irrigation_water_ph}
                  >
                    <Input
                      id="pf-iph"
                      type="number"
                      step="0.1"
                      min="0"
                      max="14"
                      value={farmForm.irrigation_water_ph}
                      onChange={update('irrigation_water_ph')}
                      placeholder="e.g. 7.2"
                    />
                  </Field>
                  <Field label="pH source" htmlFor="pf-iph-src" hint="Optional.">
                    <Input
                      id="pf-iph-src"
                      value={farmForm.irrigation_water_ph_source}
                      onChange={update('irrigation_water_ph_source')}
                      placeholder="e.g. pH meter"
                      maxLength={100}
                    />
                  </Field>
                </div>
              </div>

              {activeFarm?.updated_at && (
                <p className="profile-meta">Last updated {formatDateTime(activeFarm.updated_at)}</p>
              )}

              <div className="profile-card__actions">
                <Button variant="gold" onClick={saveFarm} disabled={savingFarm}>
                  {savingFarm ? 'Saving…' : 'Save farm details'}
                </Button>
              </div>
            </>
          )}
        </Card>
      </div>

      {/* Account actions */}
      <Card tone="surface" className="profile-card">
        <h2 className="profile-card__title">Account</h2>
        <p className="profile-account__text">
          Signing out clears your name and selected farm from this device. Your farm and
          recommendation records on the server are not deleted.
        </p>
        <div className="profile-card__actions">
          <Button variant="ghost" onClick={() => setLogoutOpen(true)}>
            Sign out
          </Button>
        </div>
      </Card>

      <ConfirmDialog
        open={logoutOpen}
        onClose={() => setLogoutOpen(false)}
        onConfirm={handleLogout}
        title="Sign out?"
        message="This clears your name and selected farm from this device. You can set them again anytime."
        confirmLabel="Sign out"
        cancelLabel="Stay"
      />
    </>
  )
}
