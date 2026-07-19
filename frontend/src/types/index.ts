export interface User {
  id: string
  full_name: string
  email: string
  role: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Patient {
  id: string
  full_name: string
  date_of_birth: string | null
  gender: string | null
  contact_info: string | null
  notes: string | null
  created_at: string
}

export interface MedDocument {
  id: string
  patient_id: string
  filename: string
  doc_type: string
  summary: string | null
  recommended_specialist: string | null
  status: 'pending' | 'processing' | 'processed' | 'failed'
  created_at: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}
