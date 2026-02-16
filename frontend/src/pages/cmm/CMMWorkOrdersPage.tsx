import { useState } from 'react'
import { Table, Card, Tag, Space, Button, Modal, Form, Select, Input, InputNumber, message, Badge, Descriptions, Row, Col } from 'antd'
import { EyeOutlined, EditOutlined, PlusOutlined, ToolOutlined, ClockCircleOutlined, PauseCircleOutlined, CheckCircleOutlined, ShoppingCartOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import PageHeader from '@/components/PageHeader'
import { useCMMWorkOrders, useUpdateInterventionStatus, useCreateIntervention } from '@/hooks/useCMM'
import { useInterventionStatusTypes } from '@/hooks/useSystemTables'
import type { CMMWorkOrderSummary, CMMInterventionSummary, InterventionStatusUpdate, InterventionCreate } from '@/types'
import './CMMWorkOrdersPage.css'

const { TextArea } = Input

/**
 * Componente per la visualizzazione degli interventi inline
 */
const InterventionsList = ({ 
  interventi, 
  onUpdateStatus,
  onAddIntervention,
  statusTypes 
}: { 
  interventi: CMMInterventionSummary[]
  onUpdateStatus: (interventionId: number, data: InterventionStatusUpdate) => void
  onAddIntervention: () => void
  statusTypes: any[]
}) => {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form] = Form.useForm()
  
  const getStatusIcon = (codice?: string) => {
    switch (codice) {
      case 'preso_in_carico': return <ToolOutlined style={{ color: '#1890ff' }} />
      case 'attesa_componente': return <ShoppingCartOutlined style={{ color: '#faad14' }} />
      case 'sospeso': return <PauseCircleOutlined style={{ color: '#ff4d4f' }} />
      case 'concluso': return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      default: return <ClockCircleOutlined style={{ color: '#8c8c8c' }} />
    }
  }
  
  const getStatusColor = (codice?: string) => {
    switch (codice) {
      case 'preso_in_carico': return 'processing'
      case 'attesa_componente': return 'warning'
      case 'sospeso': return 'error'
      case 'concluso': return 'success'
      default: return 'default'
    }
  }
  
  const handleEdit = (intervento: CMMInterventionSummary) => {
    setEditingId(intervento.id)
    form.setFieldsValue({
      stato_intervento_id: intervento.stato_intervento_id,
      note_intervento: intervento.note_intervento,
      note_sospensione: intervento.note_sospensione
    })
  }
  
  const handleSave = async (interventionId: number) => {
    try {
      const values = await form.validateFields()
      const selectedStatus = statusTypes.find(s => s.id === values.stato_intervento_id)
      
      // Verifica se lo stato richiede nota
      if (selectedStatus?.richiede_nota && !values.note_sospensione) {
        message.error('Questo stato richiede una nota descrittiva')
        return
      }
      
      onUpdateStatus(interventionId, values)
      setEditingId(null)
    } catch (error) {
      console.error('Validation error:', error)
    }
  }
  
  const handleRequestPart = (_intervento: CMMInterventionSummary) => {
    // TODO: Implementare la richiesta di acquisto componente
    message.info('Funzione richiesta acquisto in arrivo...')
  }

  return (
    <div className="interventions-list">
      <div className="interventions-header">
        <span className="interventions-title">Interventi ({interventi.length})</span>
        <Button type="link" size="small" icon={<PlusOutlined />} onClick={onAddIntervention}>
          Nuovo
        </Button>
      </div>
      
      <div className="interventions-table">
        {interventi.map((intervento) => (
          <div 
            key={intervento.id}
            className={`intervention-row ${intervento.tipo_intervento === 'Meccanico' ? 'tipo-meccanico' : 'tipo-carrozziere'} ${editingId === intervento.id ? 'editing' : ''}`}
          >
            {/* Riga principale */}
            <div className="intervention-row-main">
              <Badge 
                count={intervento.progressivo} 
                style={{ backgroundColor: intervento.tipo_intervento === 'Meccanico' ? '#1890ff' : '#722ed1' }} 
              />
              <Tag color={intervento.tipo_intervento === 'Meccanico' ? 'blue' : 'purple'} style={{ margin: '0 8px' }}>
                {intervento.tipo_intervento}
              </Tag>
              <span className="descrizione">{intervento.descrizione_intervento}</span>
              <span className="durata"><ClockCircleOutlined /> {intervento.durata_stimata}h</span>
              {intervento.stato_intervento_codice ? (
                <Tag 
                  icon={getStatusIcon(intervento.stato_intervento_codice)} 
                  color={getStatusColor(intervento.stato_intervento_codice)}
                >
                  {intervento.stato_intervento_nome}
                </Tag>
              ) : (
                <Tag>Da assegnare</Tag>
              )}
              {intervento.tipo_intervento === 'Meccanico' && (
                <Button 
                  type="text" 
                  size="small" 
                  icon={<EditOutlined />}
                  onClick={() => handleEdit(intervento)}
                />
              )}
            </div>
            
            {/* Note (se presenti) */}
            {intervento.note_intervento && (
              <div className="intervention-note">
                <strong>Nota:</strong> {intervento.note_intervento}
              </div>
            )}
            
            {/* Motivo sospensione (se sospeso) */}
            {intervento.stato_intervento_codice === 'sospeso' && intervento.note_sospensione && (
              <div className="intervention-sospensione">
                <strong>Motivo sospensione:</strong> {intervento.note_sospensione}
              </div>
            )}
            
            {/* Form modifica */}
            {editingId === intervento.id && intervento.tipo_intervento === 'Meccanico' && (
              <div className="intervention-edit-form">
                <Form form={form} layout="inline" size="small">
                  <Form.Item name="stato_intervento_id" style={{ marginBottom: 4, minWidth: 150 }}>
                    <Select placeholder="Seleziona stato">
                      {statusTypes.map(status => (
                        <Select.Option key={status.id} value={status.id}>
                          {status.nome}
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                  <Form.Item name="note_intervento" style={{ marginBottom: 4, minWidth: 200 }}>
                    <Input placeholder="Note intervento..." />
                  </Form.Item>
                  <Form.Item name="note_sospensione" style={{ marginBottom: 4, minWidth: 200 }}>
                    <Input placeholder="Motivo sospensione (se sospeso)..." />
                  </Form.Item>
                  <Button type="primary" size="small" onClick={() => handleSave(intervento.id)}>Salva</Button>
                  <Button size="small" onClick={() => setEditingId(null)}>Annulla</Button>
                  <Form.Item noStyle shouldUpdate>
                    {({ getFieldValue }) => {
                      const statoId = getFieldValue('stato_intervento_id')
                      const stato = statusTypes.find(s => s.id === statoId)
                      if (stato?.codice === 'attesa_componente') {
                        return (
                          <Button 
                            type="dashed" 
                            size="small" 
                            icon={<ShoppingCartOutlined />}
                            onClick={() => handleRequestPart(intervento)}
                          >
                            Richiedi Componente
                          </Button>
                        )
                      }
                      return null
                    }}
                  </Form.Item>
                </Form>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Pagina principale CMM Work Orders
 */
const CMMWorkOrdersPage = () => {
  const [selectedWorkOrder, setSelectedWorkOrder] = useState<CMMWorkOrderSummary | null>(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false)
  const [isNewInterventionModalOpen, setIsNewInterventionModalOpen] = useState(false)
  const [newInterventionWorkOrderId, setNewInterventionWorkOrderId] = useState<number | null>(null)
  const [newInterventionForm] = Form.useForm()
  
  const { data: workOrders, isLoading, refetch } = useCMMWorkOrders()
  const { data: statusTypes = [] } = useInterventionStatusTypes()
  const updateStatusMutation = useUpdateInterventionStatus()
  const createInterventionMutation = useCreateIntervention()
  
  const handleViewDetail = (wo: CMMWorkOrderSummary) => {
    if (!wo.ha_interventi_meccanica) {
      message.warning('Questa scheda non ha interventi di meccanica')
      return
    }
    setSelectedWorkOrder(wo)
    setIsDetailModalOpen(true)
  }
  
  const handleUpdateStatus = async (interventionId: number, data: InterventionStatusUpdate, workOrderId?: number) => {
    const woId = workOrderId || selectedWorkOrder?.id
    if (!woId) return
    
    try {
      await updateStatusMutation.mutateAsync({
        workOrderId: woId,
        interventionId,
        data
      })
      message.success('Stato intervento aggiornato')
      const result = await refetch()
      
      // Aggiorna selectedWorkOrder con i dati freschi se è aperto
      if (selectedWorkOrder && result.data) {
        const updatedWO = result.data.find(wo => wo.id === selectedWorkOrder.id)
        if (updatedWO) {
          setSelectedWorkOrder(updatedWO)
        }
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Errore aggiornamento stato')
    }
  }
  
  const handleAddIntervention = (workOrderId?: number) => {
    const woId = workOrderId || selectedWorkOrder?.id
    if (!woId) {
      message.error('Nessuna scheda lavoro selezionata')
      return
    }
    setNewInterventionWorkOrderId(woId)
    setIsNewInterventionModalOpen(true)
    newInterventionForm.resetFields()
    newInterventionForm.setFieldValue('tipo_intervento', 'Meccanico')
    newInterventionForm.setFieldValue('durata_stimata', 1)
  }
  
  const handleCreateIntervention = async () => {
    if (!newInterventionWorkOrderId) {
      message.error('Nessuna scheda lavoro selezionata')
      return
    }
    
    try {
      const values = await newInterventionForm.validateFields()
      
      const data: InterventionCreate = {
        descrizione_intervento: values.descrizione_intervento,
        durata_stimata: values.durata_stimata,
        tipo_intervento: values.tipo_intervento,
        stato_intervento_id: values.stato_intervento_id,
        note_intervento: values.note_intervento
      }
      
      await createInterventionMutation.mutateAsync({
        workOrderId: newInterventionWorkOrderId,
        data
      })
      
      message.success('Intervento creato con successo')
      setIsNewInterventionModalOpen(false)
      setNewInterventionWorkOrderId(null)
      
      // Refetch e aggiorna selectedWorkOrder se aperto
      const result = await refetch()
      if (selectedWorkOrder && result.data) {
        const updatedWO = result.data.find(wo => wo.id === selectedWorkOrder.id)
        if (updatedWO) {
          setSelectedWorkOrder(updatedWO)
        }
      }
    } catch (error: any) {
      if (error.errorFields) {
        // Errore di validazione form
        return
      }
      message.error(error.response?.data?.detail || 'Errore durante la creazione dell\'intervento')
    }
  }
  
  const getPriorityColor = (priorita?: string) => {
    switch (priorita) {
      case 'urgente': return 'red'
      case 'alta': return 'orange'
      case 'media': return 'blue'
      case 'bassa': return 'green'
      default: return 'default'
    }
  }
  
  const columns: ColumnsType<CMMWorkOrderSummary> = [
    {
      title: 'Scheda',
      dataIndex: 'numero_scheda',
      key: 'numero_scheda',
      width: 100,
      render: (text, record) => (
        <span>
          <strong>{text}</strong>{' '}
          <Tag color={getPriorityColor(record.priorita)} style={{ marginLeft: 4 }}>{record.priorita || 'media'}</Tag>
        </span>
      )
    },
    {
      title: 'Cliente',
      key: 'cliente',
      width: 150,
      render: (_, record) => (
        <span>{record.cliente_nome} {record.cliente_cognome}</span>
      )
    },
    {
      title: 'Veicolo',
      key: 'veicolo',
      width: 140,
      render: (_, record) => (
        <span><strong>{record.veicolo_targa}</strong> - {record.veicolo_marca} {record.veicolo_modello}</span>
      )
    },
    {
      title: 'Appuntamento',
      dataIndex: 'data_appuntamento',
      key: 'data_appuntamento',
      width: 100,
      render: (date) => date ? dayjs(date).format('DD/MM HH:mm') : '-'
    },
    {
      title: 'Interventi',
      key: 'interventi',
      width: 90,
      render: (_, record) => {
        const meccanici = record.interventi.filter(i => i.tipo_intervento === 'Meccanico').length
        const carrozzieri = record.interventi.filter(i => i.tipo_intervento === 'Carrozziere').length
        return (
          <span>
            {meccanici > 0 && <Tag color="blue" style={{ margin: 0 }}>M:{meccanici}</Tag>}
            {carrozzieri > 0 && <Tag color="purple" style={{ margin: '0 0 0 2px' }}>C:{carrozzieri}</Tag>}
          </span>
        )
      }
    },
    {
      title: '',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Button 
          type={record.ha_interventi_meccanica ? "primary" : "default"}
          icon={<EyeOutlined />}
          size="small"
          disabled={!record.ha_interventi_meccanica}
          onClick={() => handleViewDetail(record)}
        />
      )
    }
  ]
  
  // Expandable row per mostrare gli interventi
  const expandedRowRender = (record: CMMWorkOrderSummary) => (
    <div className="expanded-interventions">
      <InterventionsList
        interventi={record.interventi}
        onUpdateStatus={(interventionId, data) => handleUpdateStatus(interventionId, data, record.id)}
        onAddIntervention={() => handleAddIntervention(record.id)}
        statusTypes={statusTypes}
      />
    </div>
  )

  return (
    <div className="cmm-work-orders-page">
      <PageHeader
        title="Ordini di Lavoro - Meccanica"
      />
      
      <Card>
        <Table
          columns={columns}
          dataSource={workOrders || []}
          rowKey="id"
          loading={isLoading}
          expandable={{
            expandedRowRender,
            rowExpandable: (record) => record.interventi.length > 0,
          }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `${total} schede lavoro`
          }}
        />
      </Card>
      
      {/* Modal dettaglio work order */}
      <Modal
        title={
          <Space>
            <ToolOutlined />
            Dettaglio Scheda {selectedWorkOrder?.numero_scheda}
          </Space>
        }
        open={isDetailModalOpen}
        onCancel={() => setIsDetailModalOpen(false)}
        footer={null}
        width={900}
      >
        {selectedWorkOrder && (
          <div className="work-order-detail">
            {/* Sezione Cliente e Veicolo - Solo lettura */}
            <Card size="small" title="Cliente e Veicolo" className="readonly-section">
              <Descriptions column={2} size="small" bordered>
                <Descriptions.Item label="Cliente">
                  {selectedWorkOrder.cliente_nome} {selectedWorkOrder.cliente_cognome}
                </Descriptions.Item>
                <Descriptions.Item label="Telefono">
                  {selectedWorkOrder.cliente_telefono || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="Veicolo">
                  {selectedWorkOrder.veicolo_marca} {selectedWorkOrder.veicolo_modello}
                </Descriptions.Item>
                <Descriptions.Item label="Targa">
                  {selectedWorkOrder.veicolo_targa}
                </Descriptions.Item>
              </Descriptions>
            </Card>
            
            {/* Sezione Dettagli Scheda - Solo lettura */}
            <Card size="small" title="Dettagli Scheda" className="readonly-section" style={{ marginTop: 16 }}>
              <Descriptions column={2} size="small" bordered>
                <Descriptions.Item label="Numero Scheda">
                  {selectedWorkOrder.numero_scheda}
                </Descriptions.Item>
                <Descriptions.Item label="Stato">
                  <Tag color="blue">{selectedWorkOrder.stato}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Priorità">
                  <Tag color={getPriorityColor(selectedWorkOrder.priorita)}>
                    {selectedWorkOrder.priorita || 'media'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Data Appuntamento">
                  {selectedWorkOrder.data_appuntamento 
                    ? dayjs(selectedWorkOrder.data_appuntamento).format('DD/MM/YYYY HH:mm')
                    : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="Consegna Prevista" span={2}>
                  {selectedWorkOrder.data_fine_prevista 
                    ? dayjs(selectedWorkOrder.data_fine_prevista).format('DD/MM/YYYY HH:mm')
                    : '-'}
                </Descriptions.Item>
              </Descriptions>
              
              {selectedWorkOrder.note && (
                <div style={{ marginTop: 12 }}>
                  <strong>Note:</strong>
                  <p style={{ margin: '4px 0', color: '#595959' }}>{selectedWorkOrder.note}</p>
                </div>
              )}
            </Card>
            
            {/* Sezione Interventi - Editabile */}
            <Card 
              size="small" 
              title="Interventi" 
              className="editable-section" 
              style={{ marginTop: 16 }}
            >
              <InterventionsList
                interventi={selectedWorkOrder.interventi}
                onUpdateStatus={handleUpdateStatus}
                onAddIntervention={() => handleAddIntervention(selectedWorkOrder.id)}
                statusTypes={statusTypes}
              />
            </Card>
          </div>
        )}
      </Modal>
      
      {/* Modal nuovo intervento */}
      <Modal
        title="Nuovo Intervento"
        open={isNewInterventionModalOpen}
        onCancel={() => {
          setIsNewInterventionModalOpen(false)
          setNewInterventionWorkOrderId(null)
        }}
        onOk={handleCreateIntervention}
        okText="Crea Intervento"
        confirmLoading={createInterventionMutation.isPending}
      >
        <Form form={newInterventionForm} layout="vertical">
          <Form.Item 
            name="descrizione_intervento" 
            label="Descrizione"
            rules={[{ required: true, message: 'Inserisci descrizione' }]}
          >
            <TextArea rows={3} placeholder="Descrizione dell'intervento..." />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="durata_stimata" 
                label="Durata stimata (ore)"
                rules={[{ required: true, message: 'Inserisci durata' }]}
              >
                <InputNumber min={0} step={0.5} placeholder="Es: 1.5" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                name="tipo_intervento" 
                label="Tipo"
                rules={[{ required: true }]}
              >
                <Select>
                  <Select.Option value="Meccanico">Meccanico</Select.Option>
                  <Select.Option value="Carrozziere">Carrozziere</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="stato_intervento_id" label="Stato iniziale">
            <Select placeholder="Seleziona stato (opzionale)" allowClear>
              {statusTypes.map(s => (
                <Select.Option key={s.id} value={s.id}>{s.nome}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="note_intervento" label="Note">
            <TextArea rows={2} placeholder="Note opzionali..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default CMMWorkOrdersPage
