import { apiClient } from './client'
import type { AuthResponse, Patient, MedDocument, ChatMessage } from '../types'

// ---------- Auth ----------

export async function registerUser(full_name: string, email: string, password: string) {
  const { data } = await apiClient.post<AuthResponse>('/api/auth/register', {
    full_name,
    email,
    password,
  })
  return data
}

export async function loginUser(email: string, password: string) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const { data } = await apiClient.post<AuthResponse>('/api/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

// ---------- Patients ----------

export async function listPatients() {
  const { data } = await apiClient.get<Patient[]>('/api/patients')
  return data
}

export async function getPatient(id: string) {
  const { data } = await apiClient.get<Patient>(`/api/patients/${id}`)
  return data
}

export async function createPatient(payload: Partial<Patient>) {
  const { data } = await apiClient.post<Patient>('/api/patients', payload)
  return data
}

export async function deletePatient(id: string) {
  await apiClient.delete(`/api/patients/${id}`)
}

// ---------- Documents ----------

export async function listPatientDocuments(patientId: string) {
  const { data } = await apiClient.get<MedDocument[]>(`/api/documents/patient/${patientId}`)
  return data
}

export async function uploadDocument(patientId: string, file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<MedDocument>(`/api/documents/upload/${patientId}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteDocument(id: string) {
  await apiClient.delete(`/api/documents/${id}`)
}

// ---------- Chat / RAG ----------

export async function askQuestion(patientId: string, question: string) {
  const { data } = await apiClient.post<{ answer: string; sources: string[] }>('/api/chat/ask', {
    patient_id: patientId,
    question,
  })
  return data
}

export async function getChatHistory(patientId: string) {
  const { data } = await apiClient.get<ChatMessage[]>(`/api/chat/history/${patientId}`)
  return data
}
