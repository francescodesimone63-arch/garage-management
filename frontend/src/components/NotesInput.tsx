import { useState, useEffect, useRef, forwardRef } from 'react'
import { useSpeechToText } from '@/hooks/useSpeechToText'
import './NotesInput.css'

interface NotesInputProps {
  value?: string
  onChange?: (value: string) => void
}

/**
 * Componente input per note con speech-to-text integrato
 * Microfono posizionato INSIDE la textarea (come DescrizioneDannoInput)
 * Usa Web Speech API (Chrome, Edge, Firefox)
 * Lingua: it-IT
 */
const NotesInput = forwardRef<HTMLTextAreaElement, NotesInputProps>(
  ({ value = '', onChange }, ref) => {
    console.log('🔧 NotesInput render - value:', value, 'onChange:', !!onChange)

    const { transcript, isListening, startListening, stopListening, resetTranscript, error, supported } = useSpeechToText()
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const wasListeningRef = useRef<boolean>(false)
    const addedTranscriptRef = useRef<boolean>(false)

    const actualRef = ref || textareaRef

    // Gestisci la transizione isListening true -> false
    useEffect(() => {
      console.log('🔍 NotesInput useEffect isListening:', isListening, 'transcript:', transcript, 'addedTranscriptRef:', addedTranscriptRef.current)
      
      // Se siamo passati da "isListening true" a "isListening false" E abbiamo un transcript
      if (wasListeningRef.current && !isListening && transcript && !addedTranscriptRef.current) {
        console.log('✅ Aggiungo transcript al valore delle note')
        addedTranscriptRef.current = true
        const newValue = (value ? value + ' ' : '') + transcript.trim()
        console.log('📝 Nuovo valore note:', newValue)
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
      console.log('🎤 Mic clicked (Notes) - supported:', supported, 'isListening:', isListening)
      
      if (!supported) {
        alert('Speech-to-text non supportato su questo browser. Usa Chrome, Edge o Firefox moderni.')
        return
      }

      if (isListening) {
        console.log('⏹️ Fermando ascolto (Note)')
        console.log('📊 TESTO FINALE PRIMA DI FERMARE (Note):', transcript)
        stopListening()
      } else {
        console.log('🎙️ Iniziando ascolto (Note)')
        startListening()
      }
    }

    const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      onChange(e.target.value)
    }

    return (
      <div className="notes-input-container">
        <div className="notes-input-wrapper">
          <div style={{ position: 'relative' }}>
            <textarea
              ref={actualRef as any}
              className="notes-textarea"
              value={value}
              onChange={handleTextAreaChange}
              placeholder="Aggiungi note... oppure clicca il microfono per dettare"
              rows={1}
            />

            {/* Pulsante microfono - INSIDE, sempre renderizzato */}
            <div className="notes-mic-button-container">
              <button
                type="button"
                className={`notes-mic-btn ${isListening ? 'listening' : ''}`}
                onClick={handleMicClick}
                title={isListening ? 'Ferma registrazione' : 'Avvia registrazione vocale note'}
                disabled={!supported}
                aria-label={isListening ? 'Ferma registrazione vocale note' : 'Avvia registrazione vocale note'}
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
              <div className="notes-speech-status">
                <span className="notes-listening-dot" />
                🎤 Ascolto... parla ora
              </div>
            )}

            {error && <div className="notes-speech-error">{error}</div>}

            {!isListening && transcript && (
              <div className="notes-speech-status" style={{ background: '#f6ffed', border: '1px solid #b7eb8f', color: '#274d00' }}>
                ✓ Testo riconosciuto e aggiunto
              </div>
            )}
          </>
        ) : (
          <div className="notes-speech-warning">
            Speech-to-text non supportato su questo browser.
          </div>
        )}
      </div>
    )
  }
)

NotesInput.displayName = 'NotesInput'

export default NotesInput
