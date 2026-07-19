import { useState, useEffect, FormEvent } from 'react'
import type { Patient } from '../types'
import { listPatients, createPatient } from '../api/endpoints'
import PatientCard from '../components/PatientCard'

export default function Dashboard() {
  const [patients, setPatients] = useState<Patient[]>([])
  const [showForm, setShowForm] = useState(false)
  const [fullName, setFullName] = useState('')
  const [dob, setDob] = useState('')
  const [gender, setGender] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    refresh()
  }, [])

  async function refresh() {
    setLoading(true)
    const data = await listPatients()
    setPatients(data)
    setLoading(false)
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    await createPatient({ full_name: fullName, date_of_birth: dob || null, gender: gender || null })
    setFullName('')
    setDob('')
    setGender('')
    setShowForm(false)
    refresh()
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-medium text-ink">Patients</h1>
          <p className="mt-1 text-sm text-slate-300">Manage patient records and AI-processed documents.</p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-md bg-teal-500 px-4 py-2 text-sm font-medium text-white hover:bg-teal-600"
        >
          {showForm ? 'Cancel' : 'Add patient'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mt-6 grid grid-cols-1 gap-4 rounded-xl border border-slate-200 bg-white p-5 sm:grid-cols-3">
          <input
            required
            placeholder="Full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-400"
          />
          <input
            type="date"
            placeholder="Date of birth"
            value={dob}
            onChange={(e) => setDob(e.target.value)}
            className="rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-400"
          />
          <input
            placeholder="Gender"
            value={gender}
            onChange={(e) => setGender(e.target.value)}
            className="rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-400"
          />
          <button
            type="submit"
            className="col-span-full rounded-md bg-ink py-2 text-sm font-medium text-white hover:opacity-90 sm:col-span-1"
          >
            Save patient
          </button>
        </form>
      )}

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <p className="text-sm text-slate-300">Loading…</p>
        ) : patients.length === 0 ? (
          <p className="text-sm text-slate-300">No patients yet. Add your first patient to get started.</p>
        ) : (
          patients.map((p) => <PatientCard key={p.id} patient={p} />)
        )}
      </div>
    </div>
  )
}
