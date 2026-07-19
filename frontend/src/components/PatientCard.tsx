import { Link } from 'react-router-dom'
import type { Patient } from '../types'

export default function PatientCard({ patient }: { patient: Patient }) {
  return (
    <Link
      to={`/patients/${patient.id}`}
      className="block rounded-xl border border-slate-200 bg-white p-5 transition hover:border-teal-400 hover:shadow-sm"
    >
      <h3 className="font-medium text-ink">{patient.full_name}</h3>
      <p className="mt-1 text-sm text-slate-300">
        {patient.gender ?? 'Unspecified'} · {patient.date_of_birth ?? 'DOB unknown'}
      </p>
      {patient.notes && <p className="mt-2 line-clamp-2 text-sm text-slate-300">{patient.notes}</p>}
    </Link>
  )
}
