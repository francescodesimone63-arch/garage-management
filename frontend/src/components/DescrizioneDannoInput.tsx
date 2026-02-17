import { useState, useEffect, useRef, forwardRef } from 'react'
import { useSpeechToText } from '@/hooks/useSpeechToText'
import './DescrizioneDannoInput.css'

interface DescrizioneDannoInputProps {
  value?: string
  onChange?: (value: string) => void
}

/**
 * Componente input per descrizione danno con speech-to-text integrato
 * Usa Web Speech API (Chrome, Edge, Firefox)
 * Lingua: it-IT
 */
const DescrizioneDannoInput = forwardRef<HTMLTextAreaElement, DescrizioneDannoInputProps>(
  ({ value = '', onChange }, ref) => {
    console.log('🔧 DescrizioneDannoInput render - value:', value, 'onChange:', !!onChange)

    const { transcript, isListening, startListening, stopListening, resetTranscript, error, supported } = useSpeechToText()
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const wasListeningRef = useRef<boolean>(false)  // Traccia lo stato precedente
    const addedTranscriptRef = useRef<boolean>(false)  // Flag per evitare duplicati

    // Usa il ref passato o il ref locale
    const actualRef = ref || textareaRef

  // Gestisci la transizione isListening true -> false
  useEffect(() => {
    console.log('🔍 useEffect isListening:', isListening, 'transcript:', transcript, 'addedTranscriptRef:', addedTranscriptRef.current)
    
    // Se siamo passati da "isListening true" a "isListening false" E abbiamo un transcript
    if (wasListeningRef.current && !isListening && transcript && !addedTranscriptRef.current) {
      console.log('✅ Aggiungo transcript al valore')
      addedTranscriptRef.current = true
      const newValue = (value ? value + ' ' : '') + transcript.trim()
      console.log('📝 Nuovo valore:', newValue)
      onChange?.(newValue)
      resetTranscript()
    }
    
    // Resetta il flag quando il transcript viene azzerato (inizio nuova sessione)
    if (transcript === '' && addedTranscriptRef.current) {
      console.log('🔄 Transcript azzerato - resetto flag per la prossima registrazione')
      addedTranscriptRef.current = false
    }
    
    // Aggiorna lo stato precedente
    wasListeningRef.current = isListening
  }, [isListening, transcript, value, onChange, resetTranscript])

  const handleMicClick = () => {
    console.log('🎤 Mic clicked - supported:', supported, 'isListening:', isListening)
    
    if (!supported) {
      alert('Speech-to-text non supportato su questo browser. Usa Chrome, Edge o Firefox moderni.')
      return
    }

    if (isListening) {
      console.log('⏹️ Fermando ascolto')
      console.log('📊 TESTO FINALE PRIMA DI FERMARE:', transcript)
      stopListening()
    } else {
      console.log('🎙️ Iniziando ascolto')
      startListening()
    }
  }

  const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value)
  }

  return (
    <div className="descrizione-danno-container">
      <div className="descrizione-danno-wrapper">
        <div style={{ position: 'relative' }}>
          <textarea
            ref={actualRef as any}
            className="descrizione-danno-textarea"
            value={value}
            onChange={handleTextAreaChange}
            placeholder="Clicca il microfono e descrivi a voce il danno... oppure digita manualmente"
            rows={3}
          />

          {/* Pulsante microfono */}
          <div className="mic-button-container">
            <button
              type="button"
              className={`mic-btn ${isListening ? 'listening' : ''}`}
              onClick={handleMicClick}
              title={isListening ? 'Ferma registrazione' : 'Avvia registrazione vocale'}
              disabled={!supported}
              aria-label={isListening ? 'Ferma registrazione vocale' : 'Avvia registrazione vocale'}
            >
              {isListening ? '⏹️' : '🎤'}
            </button>
          </div>
        </div>
      </div>

      {/* Messaggi di stato e errore */}
      {supported ? (
        <>
          {isListening && (
            <div className="speech-status">
              <span className="listening-dot" />
              🎤 Ascolto... parla ora
            </div>
          )}

          {error && <div className="speech-error">{error}</div>}

          {!isListening && transcript && (
            <div className="speech-status" style={{ background: '#f6ffed', border: '1px solid #b7eb8f', color: '#274d00' }}>
              ✓ Testo riconosciuto e aggiunto
            </div>
          )}
        </>
      ) : (
        <div className="speech-warning">
          Speech-to-text non supportato su questo browser. Usa Chrome, Edge o Firefox moderni su desktop per usare il riconoscimento vocale.
        </div>
      )}

      {/* Info badge */}
      {supported && (
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px' }}>
          <span className="info-badge">💡 it-IT</span>
          <small style={{ color: '#8c8c8c' }}>Lingua: italiano • Supportato: Chrome, Edge, Firefox</small>
        </div>
      )}
    </div>
  )
}
)

DescrizioneDannoInput.displayName = 'DescrizioneDannoInput'

export default DescrizioneDannoInput
