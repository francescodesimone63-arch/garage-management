import { useState, useRef, useCallback, useEffect } from 'react'

interface UseSpeechToTextResult {
  transcript: string
  isListening: boolean
  startListening: () => void
  stopListening: () => void
  resetTranscript: () => void
  error: string | null
  supported: boolean
}

/**
 * Hook per speech-to-text usando Web Speech API (supporta Chrome/Edge/Firefox)
 * Lingua: it-IT (italiano)
 * @returns UseSpeechToTextResult
 */
export const useSpeechToText = (): UseSpeechToTextResult => {
  const [transcript, setTranscript] = useState<string>('')
  const [isListening, setIsListening] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [supported, setSupported] = useState<boolean>(true)

  const recognitionRef = useRef<any>(null)

  // Verifica supporto al mount
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      setSupported(false)
      setError('Speech-to-text non supportato su questo browser. Usa Chrome o Edge.')
      return
    }

    setSupported(true)
    setError(null)
  }, [])

  const startListening = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      setSupported(false)
      setError('Speech-to-text non supportato su questo browser. Usa Chrome o Edge.')
      return
    }

    // Azzera stato precedente
    setTranscript('')
    setError(null)

    // Cleanup dell'istanza precedente se esiste
    if (recognitionRef.current) {
      console.warn('🧹 Cleanuppo istanza PRECEDENTE di SpeechRecognition')
      try {
        recognitionRef.current.abort()
      } catch (err) {
        console.error('Errore durante abort della vecchia istanza:', err)
      }
    }

    // Crea nuova istanza
    console.log('🆕 Creando NUOVA istanza di SpeechRecognition')
    const recognition = new SpeechRecognition()
    recognitionRef.current = recognition
    console.log('✅ Istanza creata e assegnata a ref')

    // Dichiarazione anticipata del timeout
    let debugTimeout: NodeJS.Timeout | null = null

    // Configurazione
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 1
    recognition.lang = 'it-IT'

    // Event: inizio ascolto
    recognition.onstart = () => {
      console.log('🎤 Speech recognition avviato - ora aspetto il parlato...')
      console.log('📢 PARLA ADESSO - Il browser sta ascoltando!')
      console.log('🔧 State at onstart:', {
        continuous: recognition.continuous,
        interimResults: recognition.interimResults,
        lang: recognition.lang,
      })
      
      // Imposta timeout di debug quando inizia l'ascolto
      debugTimeout = setTimeout(() => {
        console.warn('⚠️ ATTENZIONE: Nessun risultato ricevuto dopo 3 secondi!')
        console.warn('Possibili cause:')
        console.warn('1. Permessi microfono negati')
        console.warn('2. Nessun audio rilevato')
        console.warn('3. Errore del browser nella cattura audio')
      }, 3000)
      
      setIsListening(true)
      setError(null)
    }

    // Event: risultati
    recognition.onresult = (event: any) => {
      console.log('📋 onresult triggered - resultIndex:', event.resultIndex, 'results.length:', event.results.length)
      
      let interimTranscript = ''
      let finalTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        console.log(`📝 Result ${i}: isFinal=${event.results[i].isFinal}, transcript="${transcript}"`)

        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' '
        } else {
          interimTranscript += transcript
        }
      }

      // Aggiorna transcript (mostra sia testo finale che intermedio)
      const newTranscript = finalTranscript + interimTranscript
      console.log('✍️ Aggiornato transcript:', newTranscript)
      console.log('📊 Stato transcript - finale:', finalTranscript.trim(), 'intermedio:', interimTranscript)
      setTranscript(newTranscript)
    }

    // Event: errore
    recognition.onerror = (event: any) => {
      console.error('❌ Speech recognition error:', event.error)
      console.log('📊 Errore dettagli:', {
        error: event.error,
        isSpeechFinal: event.isSpeechFinal,
        resultIndex: event.resultIndex,
      })
      
      if (event.error === 'not-allowed') {
        console.error('🔴 PERMESSO MICROFONO NEGATO!')
        console.error('Soluzione: System Preferences → Security & Privacy → Microphone → Autorizza browser')
        setError('Permesso microfono negato. Abilita l\'accesso al microfono nelle impostazioni del browser.')
      } else if (event.error === 'network') {
        setError('Errore di rete. Controlla la connessione internet.')
      } else if (event.error === 'no-speech') {
        setError('Nessun parlato rilevato. Riprova.')
      } else {
        setError(`Errore riconoscimento vocale: ${event.error}`)
      }
      setIsListening(false)
    }

    // Event: fine
    recognition.onend = () => {
      console.log('🎤 Speech recognition terminato')
      if (debugTimeout) clearTimeout(debugTimeout)
      setIsListening(false)
    }

    // Event: fine del parlato (opzionale - quando l'utente smette di parlare)
    recognition.onspeechend = () => {
      console.log('🤐 Fine del parlato rilevata dal browser - ora elaboro il testo...')
    }

    // Avvia
    try {
      recognition.start()
      console.log('✅ recognition.start() chiamato')
      
      // Debug: log gli audio context
      if ((window as any).AudioContext) {
        console.log('✅ AudioContext disponibile')
      } else if ((window as any).webkitAudioContext) {
        console.log('✅ webkitAudioContext disponibile')
      } else {
        console.warn('⚠️ Nessun AudioContext disponibile')
      }
    } catch (err) {
      console.error('❌ Errore durante start:', err)
      setError('Errore durante l\'avvio del riconoscimento vocale.')
    }
  }, [])

  const stopListening = useCallback(() => {
    console.log('🛑 stopListening called - recognitionRef.current:', !!recognitionRef.current)
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
        console.log('✅ SpeechRecognition.stop() eseguito')
      } catch (err) {
        console.error('❌ Errore durante stop:', err)
      }
    } else {
      console.warn('⚠️ recognitionRef.current è null')
    }
    setIsListening(false)
  }, [])

  const resetTranscript = useCallback(() => {
    setTranscript('')
  }, [])

  // Cleanup al unmount
  useEffect(() => {
    return () => {
      console.log('🧹 Cleanup: fermando SpeechRecognition')
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch (err) {
          console.error('Errore durante cleanup:', err)
        }
      }
    }
  }, [])

  return {
    transcript,
    isListening,
    startListening,
    stopListening,
    resetTranscript,
    error,
    supported,
  }
}
