import React, { useState, useEffect } from 'react'

export default function App() {
  const [user, setUser] = useState<any>(null)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [resource, setResource] = useState('locations')
  const [file, setFile] = useState<File | null>(null)
  const [importResult, setImportResult] = useState<any>(null)

  const getCsrfToken = () => {
    const match = document.cookie.match(/csrftoken=([^;]+)/)
    return match ? match[1] : ''
  }

  useEffect(() => {
    fetch('/api/v1/auth/csrf/')
      .then(res => res.json())
      .catch(() => {})

    fetch('/api/v1/auth/me/')
      .then(res => res.ok ? res.json() : null)
      .then(data => data && setUser(data))
      .catch(() => {})
  }, [])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const csrf = getCsrfToken()
      const res = await fetch('/api/v1/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrf,
        },
        body: JSON.stringify({ username, password }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error?.message || 'Login gagal.')
      } else {
        setUser(data.user)
      }
    } catch {
      setError('Terjadi kesalahan koneksi.')
    }
  }

  const handleLogout = async () => {
    await fetch('/api/v1/auth/logout/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } })
    setUser(null)
  }

  const handleImport = async (mode: 'preview' | 'commit') => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('resource', resource)
    formData.append('mode', mode)

    const res = await fetch('/api/v1/imports/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
      body: formData,
    })
    const data = await res.json()
    setImportResult(data)
  }

  if (!user) {
    return (
      <div style={{ padding: 40, fontFamily: 'sans-serif', maxWidth: 400, margin: 'auto' }}>
        <h2>NetLab Manager — Login</h2>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
          <button type="submit">Masuk</button>
        </form>
      </div>
    )
  }

  return (
    <div style={{ padding: 40, fontFamily: 'sans-serif', maxWidth: 800, margin: 'auto' }}>
      <h1>NetLab Manager Dashboard</h1>
      <p>Halo, <b>{user.username}</b> (Peran: {user.role})</p>
      <button onClick={handleLogout}>Keluar</button>

      <hr style={{ margin: '20px 0' }} />

      <h3>Impor CSV</h3>
      <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
        <select value={resource} onChange={e => setResource(e.target.value)}>
          <option value="locations">Locations</option>
          <option value="assets">Assets</option>
          <option value="subnets">Subnets</option>
          <option value="ip-addresses">IP Addresses</option>
        </select>
        <input type="file" accept=".csv" onChange={e => e.target.files && setFile(e.target.files[0])} />
        <button onClick={() => handleImport('preview')}>Preview</button>
        <button onClick={() => handleImport('commit')}>Commit</button>
      </div>

      {importResult && (
        <pre style={{ background: '#f4f4f4', padding: 12, borderRadius: 4 }}>
          {JSON.stringify(importResult, null, 2)}
        </pre>
      )}
    </div>
  )
}
