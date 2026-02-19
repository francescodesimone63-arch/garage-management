import { forwardRef, useMemo } from 'react'
import { useSpeechToText } from '@/hooks/useSpeechToText'
import './NotesInput.css'

interface NotesInputProps {
  value?: string
  onChange?: (value: string) => void
}

/**
 * COMPONENTE: Notes Input
 * 
 * Input textarea per note con speech-to-text integrato
 * Basato su react-speech-recognition (semplice, affidabile, zero complicazioni)
 * 
 * FUNZIONALITÀ:
 * - Scrivi manualmente o clicca il microfono
 * - Il testo appare ISTANTANEAMENTE mentre parli
 * - Testo completo e accurato
 * - Lingua: italiano
 */
const NotesInput = forwardRef<HTMLTextAreaElement, NotesInputProps>(
  ({ value = '', onChange }, ref) => {
    // ID univoco per questa istanza
    const instanceId = useMemo(() => 'notes-input', [])
    
    // Hook speech-to-text
    const { transcript, isListening, startListening, stopListening, error, supported } = useSpeechToText(instanceId)

    const handleMicClick = () => {
      if (!supported) {
        alert('Speech-to-text non supportato su questo browser. Usa Chrome, Edge o Firefox moderni.')
        return
      }

      if (isListening) {
        console.log('⏹️ Stop microfono')
        stopListening()
        // Aggiungi il testo finale al campo
        if (transcript) {
          const newValue = (value ? value + ' ' : '') + transcript.trim()
          onChange?.(newValue)
        }
      } else {
        console.log('🎤 Start microfono')
        startListening()
      }
    }

    const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      onChange?.(e.target.value)
    }

    // Valore visualizzato: il valore salvato + il testo che stai dicendo (durante l'ascolto)
    const displayValue = isListening && transcript ? value + (value ? ' ' : '') + transcript : value

    return (
      <div className="notes-input-container">
        <div className="notes-input-wrapper">
          <div style={{ position: 'relative' }}>
            <textarea
              ref={ref}
              className="notes-textarea"
              value={displayValue}
              onChange={handleTextAreaChange}
              placeholder="Aggiungi note... oppure clicca il microfono per dettare"
              rows={1}
            />

            {/* Pulsante microfono */}
            <div className="notes-mic-button-container">
              <button
                type="button"
                className={`notes-mic-btn ${isListening ? 'listening' : ''}`}
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

        {/* Messaggi di stato */}
        {supported ? (
          <>
            {isListening && (
              <div className="notes-speech-status">
                <span className="notes-listening-dot" />
                🎤 Ascolto... parla ora
              </div>
            )}
            {error && <div className="notes-speech-error">{error}</div>}
          </>
        ) : (
          <div className="notes-speech-warning">Speech-to-text non supportato su questo browser.</div>
        )}
      </div>
    )
  }
)

NotesInput.displayName = 'NotesInput'

export default NotesInput
