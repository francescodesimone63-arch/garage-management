import React, { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS, TOKEN_KEY } from '@/config/api'
import type { User, LoginRequest, LoginResponse } from '@/types'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  // Carica utente al mount
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      loadUser()
    } else {
      setLoading(false)
    }
  }, [])

  const loadUser = async () => {
    try {
      const response = await axiosInstance.get<User>(API_ENDPOINTS.ME)
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials: LoginRequest) => {
    try {
      console.log('🔐 Login attempt:', { username: credentials.username })
      setLoading(true)
      
      // Invia JWT JSON body
      const response = await axiosInstance.post<LoginResponse>(
        API_ENDPOINTS.LOGIN,
        {
          username: credentials.username,
          password: credentials.password,
        }
      )

      console.log('✅ Login response:', response.data)
      const { access_token, user: userData } = response.data

      // Salva token
      localStorage.setItem(TOKEN_KEY, access_token)
      setUser(userData)

      message.success(`Benvenuto, ${userData.nome}!`)
      console.log('🚀 Navigating to /dashboard')
      navigate('/dashboard')
    } catch (error: any) {
      console.error('❌ Login error:', error)
      if (error.response?.status === 401) {
        message.error('Email o password non corretti')
      } else {
        message.error('Errore durante il login')
      }
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
    message.info('Logout effettuato con successo')
    navigate('/login')
  }

  const refreshUser = async () => {
    await loadUser()
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
