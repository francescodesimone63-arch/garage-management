import { createContext, useContext, useState, ReactNode } from 'react'

interface SpeechContextType {
  activeInstanceId: string | null
  setActiveInstanceId: (id: string | null) => void
}

const SpeechContext = createContext<SpeechContextType | undefined>(undefined)

export const SpeechProvider = ({ children }: { children: ReactNode }) => {
  const [activeInstanceId, setActiveInstanceId] = useState<string | null>(null)

  return (
    <SpeechContext.Provider value={{ activeInstanceId, setActiveInstanceId }}>
      {children}
    </SpeechContext.Provider>
  )
}

export const useSpeechContext = () => {
  const context = useContext(SpeechContext)
  if (!context) {
    throw new Error('useSpeechContext deve essere usato dentro <SpeechProvider>')
  }
  return context
}
