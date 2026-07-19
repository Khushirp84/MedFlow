import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="text-lg font-medium text-teal-600">
          MedFlow
        </Link>
        {user && (
          <div className="flex items-center gap-6 text-sm text-slate-300">
            <Link to="/" className="hover:text-ink">
              Dashboard
            </Link>
            <span className="text-ink">{user.full_name}</span>
            <button onClick={handleLogout} className="rounded-md border border-slate-200 px-3 py-1.5 hover:bg-slate-50">
              Log out
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
