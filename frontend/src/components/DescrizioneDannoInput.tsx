import { forwardRef, useMemo } from 'react'
import { useSpeechToText } from '@/hooks/useSpeechToText'
import './DescrizioneDannoInput.css'

interface DescrizioneDannoInputProps {
  value?: string
  onChange?: (value: string) => void
}

/**
 * COMPONENTE: Descrizione Danno Input
 * 
 * Input textarea con speech-to-text integrato
 * Basato su react-speech-recognition (semplice, affidabile, zero complicazioni)
 * 
 * FUNZIONALITÀ:
 * - Scrivi manualmente o clicca il microfono
 * - Il testo appare ISTANTANEAMENTE mentre parli
 * - Testo completo e accurato
 * - Lingua: italiano
 */
const DescrizioneDannoInput = forwardRef<HTMLTextAreaElement, DescrizioneDannoInputProps>(
  ({ value = '', onChange }, ref) => {
    // ID univoco per questa istanza
    const instanceId = useMemo(() => 'descrizione-danno-input', [])
    
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
      <div className="descrizione-danno-container">
        <div className="descrizione-danno-wrapper">
          <div style={{ position: 'relative' }}>
            <textarea
              ref={ref}
              className="descrizione-danno-textarea"
              value={displayValue}
              onChange={handleTextAreaChange}
              placeholder="Clicca il microfono e descrivi il danno... oppure digita manualmente"
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

        {/* Messaggi di stato */}
        {supported ? (
          <>
            {isListening && (
              <div className="speech-status">
                <span className="listening-dot" />
                🎤 Ascolto... parla ora
              </div>
            )}
            {error && <div className="speech-error">{error}</div>}
          </>
        ) : (
          <div className="speech-warning">Speech-to-text non supportato su questo browser.</div>
        )}
      </div>
    )
  }
)

DescrizioneDannoInput.displayName = 'DescrizioneDannoInput'

export default DescrizioneDannoInput
