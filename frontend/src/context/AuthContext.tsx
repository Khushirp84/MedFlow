import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type { User } from '../types'
import { loginUser, registerUser } from '../api/endpoints'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (fullName: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('medflow_user')
    if (stored) setUser(JSON.parse(stored))
    setLoading(false)
  }, [])

  async function login(email: string, password: string) {
    const data = await loginUser(email, password)
    localStorage.setItem('medflow_token', data.access_token)
    localStorage.setItem('medflow_user', JSON.stringify(data.user))
    setUser(data.user)
  }

  async function register(fullName: string, email: string, password: string) {
    const data = await registerUser(fullName, email, password)
    localStorage.setItem('medflow_token', data.access_token)
    localStorage.setItem('medflow_user', JSON.stringify(data.user))
    setUser(data.user)
  }

  function logout() {
    localStorage.removeItem('medflow_token')
    localStorage.removeItem('medflow_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
