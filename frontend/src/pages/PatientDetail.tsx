import { useState, useEffect, useRef, ChangeEvent } from 'react'
import { useParams, Link } from 'react-router-dom'
import type { Patient, MedDocument } from '../types'
import { getPatient, listPatientDocuments, uploadDocument, deleteDocument } from '../api/endpoints'
import DocumentList from '../components/DocumentList'
import ChatBox from '../components/ChatBox'

export default function PatientDetail() {
  const { id } = useParams<{ id: string }>()
  const [patient, setPatient] = useState<Patient | null>(null)
  const [documents, setDocuments] = useState<MedDocument[]>([])
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (id) refresh(id)
  }, [id])

  // Poll for status updates while any document is still processing
  useEffect(() => {
    if (!id) return
    const hasPending = documents.some((d) => d.status === 'pending' || d.status === 'processing')
    if (!hasPending) return
    const interval = setInterval(() => refreshDocuments(id), 4000)
    return () => clearInterval(interval)
  }, [id, documents])

  async function refresh(patientId: string) {
    const [p, docs] = await Promise.all([getPatient(patientId), listPatientDocuments(patientId)])
    setPatient(p)
    setDocuments(docs)
  }

  async function refreshDocuments(patientId: string) {
    setDocuments(await listPatientDocuments(patientId))
  }

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    if (!id || !e.target.files?.[0]) return
    setUploading(true)
    try {
      await uploadDocument(id, e.target.files[0])
      await refreshDocuments(id)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  async function handleDelete(docId: string) {
    if (!id) return
    await deleteDocument(docId)
    await refreshDocuments(id)
  }

  if (!patient) return <div className="p-10 text-sm text-slate-300">Loading…</div>

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <Link to="/" className="text-sm text-teal-600">
        ← Back to patients
      </Link>

      <div className="mt-3 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-medium text-ink">{patient.full_name}</h1>
          <p className="mt-1 text-sm text-slate-300">
            {patient.gender ?? 'Unspecified'} · {patient.date_of_birth ?? 'DOB unknown'}
          </p>
        </div>
        <label className="cursor-pointer rounded-md bg-teal-500 px-4 py-2 text-sm font-medium text-white hover:bg-teal-600">
          {uploading ? 'Uploading…' : 'Upload document'}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={handleFileChange}
            className="hidden"
            disabled={uploading}
          />
        </label>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div>
          <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-300">Documents</h2>
          <DocumentList documents={documents} onDelete={handleDelete} />
        </div>
        <div className="h-[32rem]">
          <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-300">Ask about this patient</h2>
          <div className="h-[calc(100%-2rem)]">
            <ChatBox patientId={patient.id} />
          </div>
        </div>
      </div>
    </div>
  )
}
