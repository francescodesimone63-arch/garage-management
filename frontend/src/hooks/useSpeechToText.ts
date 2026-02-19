/**
 * Hook Speech-to-Text semplice e affidabile
 * Basato su react-speech-recognition library
 * 
 * FUNCTIONALITÀ:
 * - Testo appare istantaneamente mentre parli (interim results)
 * - Testo completo e accurato
 * - Lingua: it-IT (italiano)
 * - Supporto: Chrome, Edge, Firefox (moderni)
 * - Zero complicazioni, funziona subito
 * - Instance tracking: ogni campo ha il suo isListening indipendente
 * 
 * USO:
 * const { transcript, isListening, startListening, stopListening } = useSpeechToText('field-id')
 */

import { useState, useEffect } from 'react'
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition'
import { useSpeechContext } from '@/contexts/SpeechContext'

interface UseSpeechToTextResult {
  transcript: string
  isListening: boolean
  isInitializing: boolean
  startListening: () => void
  stopListening: () => void
  resetTranscript: () => void
  error: string | null
  supported: boolean
}

export const useSpeechToText = (instanceId: string): UseSpeechToTextResult => {
  const [error, setError] = useState<string | null>(null)
  const [supported, setSupported] = useState<boolean>(false)
  const [isInitializing, setIsInitializing] = useState<boolean>(false)
  const { activeInstanceId, setActiveInstanceId } = useSpeechContext()

  // Hook da react-speech-recognition
  // - transcript: il testo corrente (interim + final results)
  // - listening: se il microfono è attivo
  // - resetTranscript: resetta il testo
  // - browserSupportsSpeechRecognition: se il browser lo supporta
  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition()

  // isListening è true SOLO se QUESTO instanceId è attivo
  const isListening = activeInstanceId === instanceId && listening

  // Verifica supporto al mount
  useEffect(() => {
    console.log('🎤 useSpeechToText mounted - Browser supporta?: ', browserSupportsSpeechRecognition)
    
    if (!browserSupportsSpeechRecognition) {
      setError('Speech-to-text non supportato su questo browser. Usa Chrome, Edge o Firefox moderni.')
      setSupported(false)
    } else {
      setSupported(true)
      setError(null)
    }
  }, [browserSupportsSpeechRecognition])

  // Configura il riconoscimento vocale quando component monta
  useEffect(() => {
    const setupSpeechRecognition = () => {
      try {
        const recognition = (SpeechRecognition as any).getRecognition()
        if (recognition) {
          recognition.lang = 'it-IT'
          recognition.continuous = true
          recognition.interimResults = true
          recognition.maxAlternatives = 1
          console.log('✅ Speech Recognition configurato: lingua=it-IT, continuous=true, interimResults=true')
        }
      } catch (err) {
        console.error('❌ Errore durante setup:', err)
      }
    }

    if (supported) {
      setupSpeechRecognition()
    }
  }, [supported])

  // Quando il microfono è veramente pronto (listening === true), disattiva lo stato initializing
  useEffect(() => {
    if (isListening) {
      setIsInitializing(false)
    }
  }, [isListening])

  const startListening = () => {
    if (!supported) {
      setError('Speech-to-text non supportato su questo browser.')
      return
    }

    console.log(`🎤 [${instanceId}] Avvio ascolto... Parla adesso!`)
    // Feedback IMMEDIATO: attiva initializing
    setIsInitializing(true)
    // Imposta QUESTO instanceId come attivo
    setActiveInstanceId(instanceId)
    resetTranscript()
    setError(null)

    try {
      SpeechRecognition.startListening({ continuous: true, interimResults: true, language: 'it-IT' })
    } catch (err: any) {
      console.error('❌ Errore durante startListening:', err)
      setError(`Errore: ${err.message}`)
      setIsInitializing(false)
    }
  }

  const stopListening = () => {
    console.log(`⏹️ [${instanceId}] Stop ascolto`)
    // Disattiva initializing e activeInstanceId
    setIsInitializing(false)
    setActiveInstanceId(null)
    try {
      SpeechRecognition.stopListening()
    } catch (err: any) {
      console.error('❌ Errore durante stopListening:', err)
    }
  }

  return {
    transcript, // Il testo corrente (interim + final results, appare istantaneamente!)
    isListening, // True SOLO se questo instanceId è attivo E il mic è veramente pronto
    isInitializing, // True quando il mic è stato cliccato ma non è ancora pronto
    startListening,
    stopListening,
    resetTranscript,
    error,
    supported,
  }
}

