import React, { useState, useEffect } from 'react'
import {
  Button,
  Modal,
  Form,
  Input,
  Alert,
  Tag,
  Tooltip
} from 'antd'
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  LockOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import axiosInstance from '@/lib/axios'

interface Transition {
  to_state: string
  allowed: boolean
  reason_required: boolean
  explanation: string
  allowed_roles: string[]
  recipients: Array<{
    id: number
    name: string
    email: string
    role: string
  }>
}

interface AuditEntry {
  id: number
  from_state: string
  to_state: string
  executed_by: {
    id: number
    name: string
    role: string
  }
  reason?: string
  timestamp: string
}

interface WorkOrderStateTransitionProps {
  workOrderId: number
  currentState: string
  interventionsCount?: number
  hasDescrizione?: boolean
  onStateChange?: (newState: string) => void
}

const WorkOrderStateTransition: React.FC<WorkOrderStateTransitionProps> = ({
  workOrderId,
  currentState,
  interventionsCount = 0,
  hasDescrizione = false,
  onStateChange,
}) => {
  const [transitions, setTransitions] = useState<Transition[]>([])
  const [auditTrail, setAuditTrail] = useState<AuditEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [auditLoading, setAuditLoading] = useState(false)
  const [transitionInProgress, setTransitionInProgress] = useState(false)
  const [form] = Form.useForm()
  const [selectedTransition, setSelectedTransition] = useState<string | null>(null)
  const [reasonModalVisible, setReasonModalVisible] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Carica le transizioni disponibili
  useEffect(() => {
    loadAvailableTransitions()
    loadAuditTrail()
  }, [workOrderId, currentState, interventionsCount, hasDescrizione])

  const loadAvailableTransitions = async () => {
    try {
      setLoading(true)
      setError(null)
      console.log(`🔍 Caricamento transizioni per scheda ${workOrderId} (interventi: ${interventionsCount}, descrizione: ${hasDescrizione})...`)
      
      // Passa i valori dalla form per validazione corretta
      const params = new URLSearchParams()
      params.append('interventions_count', String(interventionsCount))
      params.append('has_descrizione', hasDescrizione ? 'true' : 'false')
      
      const response = await axiosInstance.get(
        `/work-orders/${workOrderId}/available-transitions?${params.toString()}`
      )
      console.log(`✅ Transizioni caricate:`, response.data)
      setTransitions(response.data.available_transitions || [])
    } catch (err: any) {
      console.warn(`⚠️ Impossibile caricare transizioni disponibili, usando valori vuoti:`, err.message)
      // Non propagare l'errore, permette al form di continuare
      setTransitions([])
      // Non mostrare errore all'utente se il caricamento transizioni fallisce - è non-critico
    } finally {
      setLoading(false)
    }
  }

  const loadAuditTrail = async () => {
    try {
      setAuditLoading(true)
      console.log(`🔍 Caricamento audit trail per scheda ${workOrderId}...`)
      const response = await axiosInstance.get(
        `/work-orders/${workOrderId}/audit-trail?limit=20`
      )
      console.log(`✅ Audit trail caricato:`, response.data)
      setAuditTrail(response.data.audit_trail)
    } catch (err) {
      console.error('❌ Errore nel caricamento audit trail:', err)
    } finally {
      setAuditLoading(false)
    }
  }

  const handleTransitionClick = (toState: string, requiresReason: boolean) => {
    // Validazione: blocca la transizione a "approvata" se non ci sono interventi
    if (toState === 'approvata' && interventionsCount === 0) {
      Modal.warning({
        title: 'Scheda senza interventi',
        content: 'La scheda non presenta interventi da svolgere. È necessario aggiungere almeno un intervento prima di approvare la scheda.',
        okText: 'Chiudi'
      })
      return
    }
    
    if (requiresReason) {
      setSelectedTransition(toState)
      setReasonModalVisible(true)
    } else {
      performTransition(toState, null)
    }
  }

  const performTransition = async (toState: string, reason: string | null) => {
    try {
      setTransitionInProgress(true)
      setError(null)

      // Costruisci il body della richiesta con i dati della form
      const requestBody: {
        reason?: string
        interventions_count?: number
        has_descrizione?: boolean
      } = {}
      
      if (reason) {
        requestBody.reason = reason
      }
      
      // Passa sempre i valori dalla form per validazione corretta
      requestBody.interventions_count = interventionsCount
      requestBody.has_descrizione = hasDescrizione

      await axiosInstance.post(
        `/work-orders/${workOrderId}/transition/${toState}`,
        requestBody
      )

      // Successo
      Modal.success({
        title: 'Transizione completata',
        content: `La scheda è stata spostata a: ${toState}`,
        onOk: () => {
          form.resetFields()
          setReasonModalVisible(false)
          setSelectedTransition(null)
          
          // Ricarica i dati
          loadAvailableTransitions()
          loadAuditTrail()
          
          // Notifica il parent component
          if (onStateChange) {
            onStateChange(toState)
          }
        },
      })
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Errore durante la transizione'
      setError(errorMessage)
      Modal.error({
        title: 'Errore nella transizione',
        content: errorMessage,
      })
    } finally {
      setTransitionInProgress(false)
    }
  }

  const handleReasonSubmit = async (values: { reason: string }) => {
    if (selectedTransition) {
      await performTransition(selectedTransition, values.reason)
    }
  }

  // Mapping degli stati a colori e icone
  const getStateInfo = (state: string) => {
    const stateMap: Record<string, { color: string; label: string; icon: React.ReactNode }> = {
      bozza: { color: 'default', label: 'Bozza', icon: <ClockCircleOutlined /> },
      approvata: { color: 'processing', label: 'Approvata', icon: <CheckCircleOutlined /> },
      in_lavorazione: { color: 'processing', label: 'In Lavorazione', icon: <ClockCircleOutlined /> },
      completata: { color: 'success', label: 'Completata', icon: <CheckCircleOutlined /> },
      annullata: { color: 'error', label: 'Annullata', icon: <ExclamationCircleOutlined /> },
    }
    return stateMap[state] || { color: 'default', label: state, icon: null }
  }

  // Ordine di visualizzazione degli stati
  const ALL_STATES = ['bozza', 'approvata', 'in_lavorazione', 'completata', 'annullata']

  // Normalizza lo stato corrente per il confronto
  const normalizedCurrentState = currentState.toLowerCase().replace(/\s+/g, '_')

  const currentStateInfo = getStateInfo(normalizedCurrentState)

  return (
    <div className="form-section" style={{ marginTop: '8px' }}>
      {/* Tutti gli stati in ordine */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center', marginBottom: auditTrail.length > 0 ? '12px' : 0 }}>
        <span style={{ fontSize: '12px', color: '#666', marginRight: '4px' }}>Stato:</span>
        {ALL_STATES.map((state, index) => {
          const stateInfo = getStateInfo(state)
          const isCurrentState = state === normalizedCurrentState
          const transition = transitions.find(t => t.to_state === state)
          const isTransitionAllowed = transition?.allowed === true
          const isTransitionAvailable = !!transition
          const explanation = transition?.explanation || ''
          const requiresReason = transition?.reason_required || false

          // Stato corrente - evidenziato
          if (isCurrentState) {
            return (
              <React.Fragment key={state}>
                <Tag
                  color={stateInfo.color}
                  icon={stateInfo.icon}
                  style={{ 
                    fontSize: '12px', 
                    padding: '2px 10px', 
                    margin: 0,
                    fontWeight: 'bold',
                    border: '2px solid',
                    borderColor: stateInfo.color === 'default' ? '#d9d9d9' : undefined
                  }}
                >
                  {stateInfo.label}
                </Tag>
                {index < ALL_STATES.length - 1 && (
                  <span style={{ fontSize: '11px', color: '#ccc', margin: '0 2px' }}>→</span>
                )}
              </React.Fragment>
            )
          }

          // Transizione disponibile e abilitata
          if (isTransitionAllowed) {
            return (
              <React.Fragment key={state}>
                <Tooltip title={`Sposta a: ${stateInfo.label}`}>
                  <Button
                    size="small"
                    type="primary"
                    onClick={() => handleTransitionClick(state, requiresReason)}
                    loading={transitionInProgress && selectedTransition === state}
                    style={{ fontSize: '12px', height: '24px', padding: '0 8px' }}
                  >
                    {stateInfo.label}
                  </Button>
                </Tooltip>
                {index < ALL_STATES.length - 1 && (
                  <span style={{ fontSize: '11px', color: '#ccc', margin: '0 2px' }}>→</span>
                )}
              </React.Fragment>
            )
          }

          // Transizione disponibile ma non abilitata (prerequisiti non soddisfatti o ruolo non autorizzato)
          if (isTransitionAvailable && !isTransitionAllowed) {
            return (
              <React.Fragment key={state}>
                <Tooltip title={explanation || 'Non disponibile'}>
                  <Button
                    size="small"
                    disabled
                    icon={<LockOutlined style={{ fontSize: '10px' }} />}
                    style={{ fontSize: '11px', height: '24px', padding: '0 6px' }}
                  >
                    {stateInfo.label}
                  </Button>
                </Tooltip>
                {index < ALL_STATES.length - 1 && (
                  <span style={{ fontSize: '11px', color: '#ccc', margin: '0 2px' }}>→</span>
                )}
              </React.Fragment>
            )
          }

          // Stato non raggiungibile dallo stato corrente
          return (
            <React.Fragment key={state}>
              <Tooltip title={`Non raggiungibile da "${currentStateInfo.label}"`}>
                <Button
                  size="small"
                  disabled
                  style={{ 
                    fontSize: '11px', 
                    height: '24px', 
                    padding: '0 6px',
                    opacity: 0.4
                  }}
                >
                  {stateInfo.label}
                </Button>
              </Tooltip>
              {index < ALL_STATES.length - 1 && (
                <span style={{ fontSize: '11px', color: '#ccc', margin: '0 2px' }}>→</span>
              )}
            </React.Fragment>
          )
        })}
      </div>

      {/* Errore */}
      {error && (
        <Alert
          message={error}
          type="error"
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: '8px', padding: '4px 8px', fontSize: '12px' }}
        />
      )}

      {/* Cronologia compatta */}
      {auditTrail.length > 0 && (
        <div style={{ borderTop: '1px solid #e8e8e8', paddingTop: '8px' }}>
          <div style={{ fontSize: '11px', color: '#999', marginBottom: '6px' }}>Cronologia:</div>
          <div style={{ maxHeight: '100px', overflowY: 'auto' }}>
            {auditTrail.slice(0, 5).map((entry, idx) => (
              <div key={entry.id} style={{ 
                fontSize: '11px', 
                color: '#666', 
                padding: '3px 0',
                borderBottom: idx < Math.min(auditTrail.length, 5) - 1 ? '1px solid #f5f5f5' : 'none'
              }}>
                <span style={{ color: '#999' }}>{dayjs(entry.timestamp).format('DD/MM HH:mm')}</span>
                <span style={{ margin: '0 4px' }}>·</span>
                <span>{getStateInfo(entry.from_state).label}</span>
                <span style={{ margin: '0 3px' }}>→</span>
                <span>{getStateInfo(entry.to_state).label}</span>
                <span style={{ margin: '0 4px' }}>·</span>
                <span style={{ color: '#999' }}>{entry.executed_by.name}</span>
                {entry.reason && <span style={{ fontStyle: 'italic', marginLeft: '4px' }}>"{entry.reason}"</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal per inserire il motivo */}
      <Modal
        title="Motivo della Transizione"
        open={reasonModalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setReasonModalVisible(false)
          form.resetFields()
        }}
        confirmLoading={transitionInProgress}
        width={400}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleReasonSubmit}
        >
          <Form.Item
            name="reason"
            label="Motivo"
            rules={[
              { required: true, message: 'Inserire un motivo' },
              { min: 5, message: 'Il motivo deve essere almeno di 5 caratteri' },
            ]}
          >
            <Input.TextArea
              rows={3}
              placeholder="Descrivi il motivo..."
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default WorkOrderStateTransition
