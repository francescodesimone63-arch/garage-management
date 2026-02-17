import { useEffect, useRef, forwardRef, useState } from 'react'
import { useSpeechToText } from '@/hooks/useSpeechToText'
import './VoiceTextarea.css'

interface VoiceTextareaProps {
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
  rows?: number
  minHeight?: number
  maxHeight?: number
  classNamePrefix?: string // Prefisso per i classNames (es: 'descrizione-danno', 'notes')
  label?: string // Label per info badge (es: 'Descrizione Danno', 'Note')
  debugPrefix?: string // Prefisso per log (es: 'DescrizioneDanno', 'Notes')
}

/**
 * Componente textarea generico con speech-to-text integrato
 * Riutilizzabile per qualsiasi campo che necessiti di input vocale
 * Usa Web Speech API (Chrome, Edge, Firefox)
 * Lingua: it-IT
 * 
 * IMPORTANTE: Usa uno stato interno per garantire il funzionamento anche quando
 * il Form non passa correttamente onChange
 */
const VoiceTextarea = forwardRef<HTMLTextAreaElement, VoiceTextareaProps>(
  ({
    value = '',
    onChange,
    placeholder = 'Clicca il microfono e parla... oppure digita manualmente',
    rows = 3,
    minHeight = 150,
    maxHeight = 300,
    classNamePrefix = 'voice-textarea',
    label = 'Campo',
    debugPrefix = 'VoiceTextarea',
  }, ref) => {
    // Stato interno per gestire il valore localmente INDIPENDENTEMENTE dal Form
    const [internalValue, setInternalValue] = useState<string>(value || '')

    console.log(`🔧 ${debugPrefix} render - externalValue:`, value, 'internalValue:', internalValue, 'onChange:', !!onChange)

    const { transcript, isListening, startListening, stopListening, resetTranscript, error, supported } = useSpeechToText()
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const wasListeningRef = useRef<boolean>(false)
    const addedTranscriptRef = useRef<boolean>(false)

    const actualRef = ref || textareaRef

    // Sincronizza il valore esterno (da Form) con lo stato interno
    useEffect(() => {
      if (value !== undefined && value !== internalValue) {
        console.log(`🔄 ${debugPrefix} - Sincronizzazione valore esterno:`, value)
        setInternalValue(value)
      }
    }, [value, internalValue, debugPrefix])

    // Gestisci la transizione isListening true -> false
    useEffect(() => {
      console.log(`🔍 ${debugPrefix} useEffect isListening:`, isListening, 'transcript:', transcript, 'addedTranscriptRef:', addedTranscriptRef.current, 'currentValue:', internalValue)

      // Se siamo passati da "isListening true" a "isListening false" E abbiamo un transcript
      if (wasListeningRef.current && !isListening && transcript && !addedTranscriptRef.current) {
        console.log(`✅ ${debugPrefix} - Aggiungo transcript al valore`)
        addedTranscriptRef.current = true
        
        // Crea il nuovo valore
        const newValue = (internalValue ? internalValue + ' ' : '') + transcript.trim()
        console.log(`📝 ${debugPrefix} - Nuovo valore:`, newValue)
        
        // Aggiorna SEMPRE lo stato interno (questo garantisce l'aggiornamento nel campo)
        setInternalValue(newValue)
        
        // INOLTRE chiama onChange se disponibile (per sincronizzare con il Form)
        if (onChange) {
          console.log(`📤 ${debugPrefix} - Chiamo onChange`)
          onChange(newValue)
        } else {
          console.warn(`⚠️ ${debugPrefix} - onChange non disponibile dal Form, ma lo stato interno è aggiornato`)
        }
        
        resetTranscript()
      }

      // Resetta il flag quando il transcript viene azzerato (inizio nuova sessione)
      if (transcript === '' && addedTranscriptRef.current) {
        console.log(`🔄 ${debugPrefix} - Transcript azzerato - resetto flag`)
        addedTranscriptRef.current = false
      }

      // Aggiorna lo stato precedente
      wasListeningRef.current = isListening
    }, [isListening, transcript, internalValue, onChange, resetTranscript, debugPrefix])

    const handleMicClick = () => {
      console.log(`🎤 ${debugPrefix} Mic clicked - supported:`, supported, 'isListening:', isListening)

      if (!supported) {
        alert('Speech-to-text non supportato su questo browser. Usa Chrome, Edge o Firefox moderni.')
        return
      }

      if (isListening) {
        console.log(`⏹️ ${debugPrefix} - Fermando ascolto`)
        console.log(`📊 ${debugPrefix} - TESTO FINALE PRIMA DI FERMARE:`, transcript)
        stopListening()
      } else {
        console.log(`🎙️ ${debugPrefix} - Iniziando ascolto`)
        startListening()
      }
    }

    const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value
      console.log(`✏️ ${debugPrefix} - Digitazione manuale:`, newValue)
      
      // Aggiorna lo stato interno
      setInternalValue(newValue)
      
      // Chiama onChange se disponibile
      onChange?.(newValue)
    }

    return (
      <div className={`${classNamePrefix}-container`}>
        <div className={`${classNamePrefix}-wrapper`}>
          <div style={{ position: 'relative' }}>
            <textarea
              ref={actualRef as any}
              className={`${classNamePrefix}-textarea`}
              value={internalValue}
              onChange={handleTextAreaChange}
              placeholder={placeholder}
              rows={rows}
              style={{
                minHeight: `${minHeight}px`,
                maxHeight: `${maxHeight}px`,
              }}
            />

            {/* Pulsante microfono - INSIDE, sempre renderizzato */}
            <div className={`${classNamePrefix}-mic-button-container`}>
              <button
                type="button"
                className={`${classNamePrefix}-mic-btn ${isListening ? 'listening' : ''}`}
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
              <div className={`${classNamePrefix}-speech-status`}>
                <span className={`${classNamePrefix}-listening-dot`} />
                🎤 Ascolto... parla ora
              </div>
            )}

            {error && <div className={`${classNamePrefix}-speech-error`}>{error}</div>}

            {!isListening && transcript && (
              <div className={`${classNamePrefix}-speech-status`} style={{ background: '#f6ffed', border: '1px solid #b7eb8f', color: '#274d00' }}>
                ✓ Testo riconosciuto e aggiunto
              </div>
            )}
          </>
        ) : (
          <div className={`${classNamePrefix}-speech-warning`}>
            Speech-to-text non supportato su questo browser. Usa Chrome, Edge o Firefox moderni su desktop.
          </div>
        )}

        {/* Info badge */}
        {supported && (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px' }}>
            <span className={`${classNamePrefix}-info-badge`}>💡 it-IT</span>
            <small style={{ color: '#8c8c8c' }}>Lingua: italiano • {label}</small>
          </div>
        )}
      </div>
    )
  }
)

VoiceTextarea.displayName = 'VoiceTextarea'

export default VoiceTextarea
