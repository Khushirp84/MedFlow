import type { MedDocument } from '../types'

const STATUS_STYLES: Record<MedDocument['status'], string> = {
  pending: 'bg-slate-100 text-slate-300',
  processing: 'bg-clay-400/10 text-clay-500',
  processed: 'bg-teal-50 text-teal-600',
  failed: 'bg-red-50 text-red-600',
}

export default function DocumentList({
  documents,
  onDelete,
}: {
  documents: MedDocument[]
  onDelete: (id: string) => void
}) {
  if (documents.length === 0) {
    return <p className="text-sm text-slate-300">No documents uploaded yet.</p>
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div key={doc.id} className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="font-medium text-ink">{doc.filename}</p>
              <p className="text-xs uppercase tracking-wide text-slate-300">{doc.doc_type.replace('_', ' ')}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_STYLES[doc.status]}`}>
                {doc.status}
              </span>
              <button
                onClick={() => onDelete(doc.id)}
                className="text-xs text-slate-300 hover:text-red-600"
                aria-label={`Delete ${doc.filename}`}
              >
                Delete
              </button>
            </div>
          </div>

          {doc.summary && (
            <p className="mt-3 text-sm leading-relaxed text-ink">{doc.summary}</p>
          )}

          {doc.recommended_specialist && (
            <p className="mt-2 text-sm">
              <span className="text-slate-300">Recommended specialist: </span>
              <span className="font-medium text-teal-600">{doc.recommended_specialist}</span>
            </p>
          )}
        </div>
      ))}
    </div>
  )
}
