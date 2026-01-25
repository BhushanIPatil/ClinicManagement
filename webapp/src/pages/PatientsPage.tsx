/**
 * Patients Page
 *
 * List patients and add new patients. Add a patient before setting up appointments.
 */

import { useState, useCallback } from 'react'
import { Plus } from 'lucide-react'
import { usePatients } from '@/hooks/usePatients'
import { PatientsList } from '@/components/features/PatientsList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import type { PatientCreateRequest, Gender } from '@/types/patient.types'

const GENDER_OPTIONS: Gender[] = ['MALE', 'FEMALE', 'OTHER']

export default function PatientsPage() {
  const { patients, loading, error, createPatient } = usePatients({
    autoFetch: true,
    pageSize: 50,
  })
  const [modalOpen, setModalOpen] = useState(false)
  const [formSubmitting, setFormSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [first_name, setFirst_name] = useState('')
  const [last_name, setLast_name] = useState('')
  const [date_of_birth, setDate_of_birth] = useState('')
  const [gender, setGender] = useState<Gender>('OTHER')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [address, setAddress] = useState('')
  const [emergency_contact_name, setEmergency_contact_name] = useState('')
  const [emergency_contact_phone, setEmergency_contact_phone] = useState('')
  const [blood_type, setBlood_type] = useState('')
  const [allergies, setAllergies] = useState('')

  const openAdd = useCallback(() => {
    setFirst_name('')
    setLast_name('')
    setDate_of_birth('')
    setGender('OTHER')
    setEmail('')
    setPhone('')
    setAddress('')
    setEmergency_contact_name('')
    setEmergency_contact_phone('')
    setBlood_type('')
    setAllergies('')
    setFormError(null)
    setModalOpen(true)
  }, [])

  const closeModal = useCallback(() => {
    setModalOpen(false)
    setFormError(null)
  }, [])

  const handleSubmit = useCallback(async () => {
    const fn = (first_name ?? '').trim()
    const ln = (last_name ?? '').trim()
    if (!fn || !ln) {
      setFormError('First name and last name are required.')
      return
    }
    setFormSubmitting(true)
    setFormError(null)
    try {
      const dob = (date_of_birth ?? '').trim()
      const payload: PatientCreateRequest = {
        first_name: fn,
        last_name: ln,
        date_of_birth: dob || undefined,
        gender,
        email: (email ?? '').trim() || undefined,
        phone: (phone ?? '').trim() || undefined,
        address: (address ?? '').trim() || undefined,
        emergency_contact_name: (emergency_contact_name ?? '').trim() || undefined,
        emergency_contact_phone: (emergency_contact_phone ?? '').trim() || undefined,
        blood_type: (blood_type ?? '').trim() || undefined,
        allergies: (allergies ?? '').trim() || undefined,
      }
      await createPatient(payload)
      closeModal()
    } catch (e: unknown) {
      const msg = (e as { detail?: string })?.detail ?? (e as Error)?.message ?? 'Failed to add patient'
      setFormError(String(msg))
    } finally {
      setFormSubmitting(false)
    }
  }, [
    first_name,
    last_name,
    date_of_birth,
    gender,
    email,
    phone,
    address,
    emergency_contact_name,
    emergency_contact_phone,
    blood_type,
    allergies,
    createPatient,
    closeModal,
  ])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Patients</h1>
        <Button onClick={openAdd} className="gap-2">
          <Plus className="w-4 h-4" />
          Add patient
        </Button>
      </div>
      <p className="text-muted-foreground text-sm">
        Add patients here, then set up appointments from the Appointments page.
      </p>
      <PatientsList patients={patients} loading={loading} error={error} />

      {modalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
          onClick={closeModal}
        >
          <div
            className={cn(
              glassmorphism('dark', true, true),
              'rounded-xl border border-white/20 w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-xl'
            )}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 space-y-4">
              <h2 className="text-lg font-semibold">Add patient</h2>
              {formError && <p className="text-sm text-destructive">{formError}</p>}
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-muted-foreground">First name *</label>
                  <Input
                    value={first_name}
                    onChange={(e) => setFirst_name(e.target.value)}
                    placeholder="First name"
                  />
                </div>
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-muted-foreground">Last name *</label>
                  <Input
                    value={last_name}
                    onChange={(e) => setLast_name(e.target.value)}
                    placeholder="Last name"
                  />
                </div>
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Date of birth *</label>
                <Input
                  type="date"
                  value={date_of_birth}
                  onChange={(e) => setDate_of_birth(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Gender</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={gender}
                  onChange={(e) => setGender(e.target.value as Gender)}
                >
                  {GENDER_OPTIONS.map((g) => (
                    <option key={g} value={g}>
                      {g}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Phone</label>
                <Input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Phone"
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Email</label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email"
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Address</label>
                <Input
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Address"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Emergency contact name
                  </label>
                  <Input
                    value={emergency_contact_name}
                    onChange={(e) => setEmergency_contact_name(e.target.value)}
                    placeholder="Name"
                  />
                </div>
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Emergency contact phone
                  </label>
                  <Input
                    type="tel"
                    value={emergency_contact_phone}
                    onChange={(e) => setEmergency_contact_phone(e.target.value)}
                    placeholder="Phone"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-muted-foreground">Blood type</label>
                  <Input
                    value={blood_type}
                    onChange={(e) => setBlood_type(e.target.value)}
                    placeholder="e.g. A+"
                  />
                </div>
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-muted-foreground">Allergies</label>
                  <Input
                    value={allergies}
                    onChange={(e) => setAllergies(e.target.value)}
                    placeholder="Allergies"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={closeModal} disabled={formSubmitting}>
                  Cancel
                </Button>
                <Button onClick={handleSubmit} disabled={formSubmitting}>
                  {formSubmitting ? 'Saving...' : 'Add patient'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
