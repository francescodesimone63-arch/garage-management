import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Table, Button, Modal, Form, Input, Select, Space, Tag, Popconfirm, message, InputNumber, Card, Row, Col, DatePicker, Grid, Divider } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, FileTextOutlined, UserAddOutlined, CarOutlined, CalendarOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { useQueryClient } from '@tanstack/react-query'
import PageHeader from '@/components/PageHeader'
import WorkOrderStateTransition from '@/components/WorkOrderStateTransition'
import { CalendarModal } from '@/components/CalendarModal'
import VoiceTextarea from '@/components/VoiceTextarea'
import { useWorkOrders, useCreateWorkOrder, useUpdateWorkOrder, useDeleteWorkOrder } from '@/hooks/useWorkOrders'
import { useInterventions } from '@/hooks/useInterventions'
import { useCustomers, useCreateCustomer } from '@/hooks/useCustomers'
import { useVehicles, useCreateVehicle } from '@/hooks/useVehicles'
import { usePriorityTypes, useWorkOrderStatusTypes, useCustomerTypes } from '@/hooks/useSystemTables'
import type { WorkOrder, WorkOrderStatus, Intervention, InterventionCreate } from '@/types'
import './WorkOrdersPage.css'

const { useBreakpoint } = Grid

const WorkOrdersPage = () => {
  const screens = useBreakpoint()
  const [searchParams, setSearchParams] = useSearchParams()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingWorkOrder, setEditingWorkOrder] = useState<WorkOrder | null>(null)
  const [selectedCustomerId, setSelectedCustomerId] = useState<number>()
  const editingWorkOrderId = editingWorkOrder?.id
  
  // Interventions form state
  const [formInterventions, setFormInterventions] = useState<Intervention[]>([])
  
  // Filtri per data nella lista
  const [dateFilterType, setDateFilterType] = useState<'compilazione' | 'appuntamento' | 'consegna'>('compilazione')
  const [dateFilter, setDateFilter] = useState<string>('')  // Empty = no date filter by default
  
  // Quick add modals
  const [isCustomerModalOpen, setIsCustomerModalOpen] = useState(false)
  const [isVehicleModalOpen, setIsVehicleModalOpen] = useState(false)
  
  // Calendar modal state
  const [isCalendarModalOpen, setIsCalendarModalOpen] = useState(false)
  const [displayedAppointmentDate, setDisplayedAppointmentDate] = useState<string>('')
  
  const [form] = Form.useForm()
  const [customerForm] = Form.useForm()
  const [vehicleForm] = Form.useForm()
  
  // Watch descrizione field for reactive updates
  const watchedDescrizione = Form.useWatch('descrizione', form)

  const { data, isLoading, error: workOrdersError } = useWorkOrders(page, 10, searchText, statusFilter)
  const { data: customersData, refetch: refetchCustomers } = useCustomers(1, 1000)
  const { data: vehiclesData, refetch: refetchVehicles } = useVehicles(1, 1000)
  const { interventions: dbInterventions, create: createInterventionMutation, update: updateInterventionMutation, delete: deleteInterventionMutation } = useInterventions(editingWorkOrderId)
  const { data: priorityTypes } = usePriorityTypes()
  const { data: workOrderStatusTypes } = useWorkOrderStatusTypes()
  const { data: customerTypes } = useCustomerTypes()
  const createWorkOrderMutation = useCreateWorkOrder()
  const updateWorkOrderMutation = useUpdateWorkOrder()
  const deleteWorkOrderMutation = useDeleteWorkOrder()
  const createCustomerMutation = useCreateCustomer()
  const createVehicleMutation = useCreateVehicle()

  // Determine if desktop or mobile
  const isDesktop = screens.lg ?? true
  
  // Debug logging
  useEffect(() => {
    console.log('📊 WorkOrdersPage - Data updated:', {
      dataItems: data?.items?.length || 0,
      isLoading,
      hasError: !!workOrdersError,
      error: workOrdersError?.message,
      page,
      searchText,
      statusFilter
    })
  }, [data, isLoading, workOrdersError, page, searchText, statusFilter])

  // Force refetch on component mount to ensure data loads
  useEffect(() => {
    console.log('🚀 WorkOrdersPage mounted - forcing refetch')
    queryClient.invalidateQueries({ queryKey: ['work-orders'] })
  }, [queryClient])
  
  // Filter works orders by date
  const filteredWorkOrders = data?.items?.filter(wo => {
    // If no date filter, show all
    if (!dateFilter) return true
    
    if (dateFilterType === 'compilazione') {
      return wo.data_compilazione?.startsWith(dateFilter)
    } else if (dateFilterType === 'appuntamento') {
      return wo.data_appuntamento?.startsWith(dateFilter)
    } else if (dateFilterType === 'consegna') {
      return wo.data_fine_prevista?.startsWith(dateFilter)
    }
    return true
  }) || []

  const statuses: { value: WorkOrderStatus; label: string; color: string }[] = workOrderStatusTypes?.map(st => {
    // Normalizza il nome: lowercase e sostituisce spazi con underscore
    const normalizedValue = st.nome.toLowerCase().replace(/\s+/g, '_') as WorkOrderStatus
    return {
      value: normalizedValue,
      label: st.nome.charAt(0).toUpperCase() + st.nome.slice(1).toLowerCase().replace(/_/g, ' '),
      color: normalizedValue === 'bozza' ? 'cyan' 
            : normalizedValue === 'approvata' ? 'orange'
            : normalizedValue === 'in_lavorazione' ? 'blue'
            : normalizedValue === 'completata' ? 'green'
            : 'default'
    }
  }).filter((status, index, self) => 
    // Rimuovi duplicati basandosi sul value normalizzato
    self.findIndex(s => s.value === status.value) === index
  ) || [
    { value: 'bozza' as WorkOrderStatus, label: 'Bozza', color: 'cyan' },
    { value: 'approvata' as WorkOrderStatus, label: 'Approvata', color: 'orange' },
    { value: 'in_lavorazione' as WorkOrderStatus, label: 'In Lavorazione', color: 'blue' },
    { value: 'completata' as WorkOrderStatus, label: 'Completata', color: 'green' },
    { value: 'annullata' as WorkOrderStatus, label: 'Annullata', color: 'default' },
  ]

  // Filter vehicles by selected customer
  const customerVehicles = selectedCustomerId
    ? vehiclesData?.items.filter(v => v.customer_id === selectedCustomerId)
    : vehiclesData?.items

  // Auto-open work order modal when ?id=X is in URL (e.g., after OAuth redirect)
  useEffect(() => {
    const workOrderId = searchParams.get('id')
    if (workOrderId && data?.items) {
      const workOrder = data.items.find(wo => wo.id === parseInt(workOrderId))
      if (workOrder) {
        handleEdit(workOrder)
        // Clean up URL params
        setSearchParams({})
      }
    }
  }, [searchParams, data?.items])

  // Handle calendar appointment selection or deletion
  const handleCalendarConfirm = (appointmentData: {
    appointment_date: string | null
  }) => {
    if (appointmentData.appointment_date === null) {
      // Appointment was deleted
      form.setFieldsValue({ data_appuntamento: null })
      setDisplayedAppointmentDate('')
      // Aggiorna anche editingWorkOrder per mantenere sincronizzato lo stato
      if (editingWorkOrder) {
        setEditingWorkOrder({ ...editingWorkOrder, data_appuntamento: undefined as any })
      }
      message.info('✅ Appuntamento cancellato')
    } else {
      // Appointment was booked
      form.setFieldsValue({ data_appuntamento: appointmentData.appointment_date })
      setDisplayedAppointmentDate(dayjs(appointmentData.appointment_date).format('DD/MM/YYYY'))
      // Aggiorna anche editingWorkOrder per mantenere sincronizzato lo stato
      if (editingWorkOrder) {
        setEditingWorkOrder({ ...editingWorkOrder, data_appuntamento: appointmentData.appointment_date })
      }
      message.success('✅ Appuntamento prenotato con successo')
    }
    setIsCalendarModalOpen(false)
  }

  const handleCreate = () => {
    try {
      setEditingWorkOrder(null)
      setSelectedCustomerId(undefined)
      setDisplayedAppointmentDate('')
      form.resetFields()
      const today = dayjs()
      
      // NON pre-compilare il numero_scheda - sarà generato dal backend al salvataggio
      form.setFieldsValue({
        data_compilazione: today,
        data_appuntamento: today,
        stato: 'bozza',
      })
      
      setIsModalOpen(true)
    } catch (error) {
      console.error('❌ Errore in handleCreate:', error)
      const today = dayjs()
      form.setFieldsValue({
        data_compilazione: today,
        data_appuntamento: today,
        stato: 'bozza',
      })
      setIsModalOpen(true)
    }
  }

  const handleEdit = (record: WorkOrder) => {
    setEditingWorkOrder(record)
    setSelectedCustomerId(record.customer_id)
    // Non convertire date qui - il DatePicker gestisce le stringhe YYYY-MM-DD direttamente
    // IMPORTANTE: Escludi 'interventions' e altri campi non di form per evitare errori di serializzazione
    const { interventions, created_at, updated_at, parts_count, labor_hours, total_parts_cost, total_labor_cost, customer_nome, customer_email, customer_telefono, vehicle_targa, vehicle_marca, vehicle_modello, vehicle_anno, vehicle_colore, ...formData } = record
    form.setFieldsValue(formData)
    // Aggiorna la data visualizzata per l'appuntamento
    if (record.data_appuntamento) {
      setDisplayedAppointmentDate(dayjs(record.data_appuntamento).format('DD/MM/YYYY'))
      console.log('📅 handleEdit: data_appuntamento =', record.data_appuntamento)
    } else {
      setDisplayedAppointmentDate('')
      console.log('📅 handleEdit: no appointment date')
    }
    setIsModalOpen(true)
  }

  // Quando apro la modal di modifica, sincronizza gli interventi con quelli presenti nel backend
  useEffect(() => {
    if (!isModalOpen || !editingWorkOrderId) return

    if (dbInterventions && dbInterventions.length > 0) {
      setFormInterventions(
        dbInterventions.map((intervention) => ({
          ...intervention,
          _isNew: false,
          _modified: false,
        }))
      )
    } else {
      setFormInterventions([])
    }
  }, [isModalOpen, editingWorkOrderId, dbInterventions])

  const handleDelete = async (id: number) => {
    await deleteWorkOrderMutation.mutateAsync(id)
  }

  const handleCustomerChange = (customerId: number) => {
    setSelectedCustomerId(customerId)
    form.setFieldsValue({ vehicle_id: undefined })
  }

  // Quick add customer
  const handleQuickAddCustomer = () => {
    customerForm.resetFields()
    customerForm.setFieldsValue({ tipo: 'privato' })
    setIsCustomerModalOpen(true)
  }

  const handleCustomerSubmit = async (values: any) => {
    try {
      const newCustomer = await createCustomerMutation.mutateAsync(values)
      setIsCustomerModalOpen(false)
      customerForm.resetFields()
      await refetchCustomers()
      // Auto-select the new customer
      form.setFieldsValue({ customer_id: newCustomer.id })
      setSelectedCustomerId(newCustomer.id)
      message.success('Cliente creato! Ora seleziona o crea il veicolo.')
    } catch (error) {
      message.error('Errore durante la creazione del cliente')
    }
  }

  // Quick add vehicle
  const handleQuickAddVehicle = () => {
    if (!selectedCustomerId) {
      message.warning('Seleziona prima un cliente!')
      return
    }
    vehicleForm.resetFields()
    vehicleForm.setFieldsValue({ customer_id: selectedCustomerId })
    setIsVehicleModalOpen(true)
  }

  const handleVehicleSubmit = async (values: any) => {
    try {
      const newVehicle = await createVehicleMutation.mutateAsync(values)
      setIsVehicleModalOpen(false)
      vehicleForm.resetFields()
      await refetchVehicles()
      // Auto-select the new vehicle
      form.setFieldsValue({ vehicle_id: newVehicle.id })
      message.success('Veicolo creato! Ora completa i dettagli della scheda lavoro.')
    } catch (error) {
      message.error('Errore durante la creazione del veicolo')
    }
  }

  const handleSubmit = async (values: any) => {
    try {
      // Converti i campi data vuoti in null per cancellare i valori nel backend
      const cleanedValues = { ...values }
      
      // Assicura che data_compilazione sia sempre presente (obbligatorio)
      if (!cleanedValues.data_compilazione) {
        cleanedValues.data_compilazione = dayjs().format('YYYY-MM-DD')
      }
      
      // Se data_fine_prevista è vuota, invia null (così il backend la cancella)
      if (!cleanedValues.data_fine_prevista) {
        cleanedValues.data_fine_prevista = null
      }
      
      // Se data_completamento è vuota, invia null
      if (!cleanedValues.data_completamento) {
        cleanedValues.data_completamento = null
      }
      
      // Se data_appuntamento è vuota, invia null (adesso è opzionale)
      if (!cleanedValues.data_appuntamento) {
        cleanedValues.data_appuntamento = null
      }
      
      let workOrderId: number
      let newWorkOrderData: WorkOrder | undefined = undefined
      
      // ==============================================================
      // STEP 1: Crea o aggiorna la scheda lavoro
      // ==============================================================
      try {
        if (editingWorkOrder) {
          console.log('📝 Aggiornando scheda esistente:', editingWorkOrder.id)
          await updateWorkOrderMutation.mutateAsync({ id: editingWorkOrder.id, data: cleanedValues })
          workOrderId = editingWorkOrder.id
        } else {
          // Crea nuova scheda - NON inviare numero_scheda, sarà generato dal backend
          delete cleanedValues.numero_scheda
          delete cleanedValues.data_creazione
          delete cleanedValues.created_at
          delete cleanedValues.updated_at
          
          console.log('🔍 DEBUG: cleanedValues che viene inviato:', cleanedValues)
          const result = await createWorkOrderMutation.mutateAsync(cleanedValues)
          
          // Verifica che la scheda sia stata creata con un ID valido
          if (!result?.id) {
            throw new Error('Scheda creata ma senza ID valido - contatta il supporto')
          }
          
          newWorkOrderData = result
          workOrderId = result.id
          console.log('✅ Scheda creata:', { numero: result.numero_scheda, id: result.id })
        }
      } catch (error) {
        console.error('❌ Errore nella creazione della scheda:', error)
        message.error('Errore nella creazione della scheda: ' + (error instanceof Error ? error.message : 'Errore sconosciuto'))
        throw error
      }
      
      // ==============================================================
      // STEP 2: Sincronizza gli interventi
      // ==============================================================
      try {
        if (editingWorkOrder && workOrderId) {
          console.log('📋 Sincronizzando interventi per scheda:', workOrderId)
          
          // Raccogli gli id degli interventi che rimangono
          const remainingIds = formInterventions
            .filter(i => i.id && !i._isNew)
            .map(i => i.id)
          
          // Elimina interventi che non sono più nella form
          for (const intervention of dbInterventions) {
            if (intervention.id && !remainingIds.includes(intervention.id)) {
              console.log('🗑️  Eliminando intervento:', intervention.id)
              await deleteInterventionMutation.mutateAsync({
                interventionId: intervention.id,
                workOrderId
              })
            }
          }
          
          // Crea o aggiorna interventi
          for (const intervention of formInterventions) {
            if (!intervention.id || intervention._isNew) {
              // Nuovo intervento - crealo
              console.log('➕ Creando nuovo intervento')
              const newInterventionData: InterventionCreate = {
                descrizione_intervento: intervention.descrizione_intervento,
                durata_stimata: intervention.durata_stimata,
                tipo_intervento: intervention.tipo_intervento
              }
              await createInterventionMutation.mutateAsync({
                workOrderId,
                data: newInterventionData
              })
            } else if (intervention._modified) {
              // Intervento modificato - aggiornalo
              console.log('✏️  Aggiornando intervento:', intervention.id)
              const updateData: InterventionCreate = {
                descrizione_intervento: intervention.descrizione_intervento,
                durata_stimata: intervention.durata_stimata,
                tipo_intervento: intervention.tipo_intervento
              }
              await updateInterventionMutation.mutateAsync({
                interventionId: intervention.id,
                data: {
                  ...updateData,
                  work_order_id: workOrderId
                }
              })
            }
          }
        } else if (!editingWorkOrder && workOrderId && formInterventions.length > 0) {
          // Nuova scheda con interventi - crea tutti gli interventi
          console.log('📋 Creando interventi per nuova scheda:', workOrderId, 'Totale:', formInterventions.length)
          
          for (const intervention of formInterventions) {
            const newInterventionData: InterventionCreate = {
              descrizione_intervento: intervention.descrizione_intervento,
              durata_stimata: intervention.durata_stimata,
              tipo_intervento: intervention.tipo_intervento
            }
            console.log('➕ Creando intervento:', newInterventionData.descrizione_intervento)
            await createInterventionMutation.mutateAsync({
              workOrderId,
              data: newInterventionData
            })
          }
        } else if (!editingWorkOrder && workOrderId && formInterventions.length === 0) {
          console.log('ℹ️  Nessun intervento da salvare')
        }
      } catch (error) {
        console.error('❌ Errore nel salvataggio degli interventi:', error)
        
        // Se è una nuova scheda, avvisa l'utente che la scheda fue creata ma ci sono problemi con gli interventi
        if (newWorkOrderData) {
          message.warning(`⚠️  Scheda ${newWorkOrderData.numero_scheda} creata, ma errore nel salvataggio degli interventi`)
          console.log('⚠️  La scheda è stata creata comunque, contatta il supporto per gli interventi')
        } else {
          message.error('Errore nel salvataggio degli interventi: ' + (error instanceof Error ? error.message : 'Errore sconosciuto'))
        }
        
        // Non re-throw l'errore se la scheda è stata creata - permetti all'utente di continuare
        if (!newWorkOrderData) {
          throw error
        }
      }
      
      // ==============================================================
      // STEP 3: Chiudi la modal e mostra messaggio di successo
      // ==============================================================
      setIsModalOpen(false)
      form.resetFields()
      setSelectedCustomerId(undefined)
      setFormInterventions([])
      
      // Mostra messaggio di successo SOLO se tutto ha funzionato
      if (newWorkOrderData) {
        message.success(`✅ Scheda creata con numero: ${newWorkOrderData.numero_scheda}`)
      } else if (editingWorkOrder) {
        message.success('✅ Scheda aggiornata')
      }
    } catch (error) {
      console.error('❌ Errore durante il salvataggio:', error)
      message.error('Errore durante il salvataggio')
    }
  }

  // LAYOUT #1: Desktop - Minimalista Orizzontale (Compact)
  const desktopColumns: ColumnsType<WorkOrder> = [
    {
      title: 'N° Scheda',
      dataIndex: 'numero_scheda',
      key: 'numero_scheda',
      width: 100,
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Cliente',
      key: 'customer',
      width: 120,
      render: (_, record) =>
        record.customer_nome || (record.customer ? `${record.customer.nome} ${record.customer.cognome}` : '-'),
    },
    {
      title: 'Veicolo',
      key: 'vehicle',
      width: 140,
      render: (_, record) => {
        const targa = record.vehicle_targa || record.vehicle?.targa || ''
        const marca = record.vehicle_marca || record.vehicle?.marca || ''
        const modello = record.vehicle_modello || record.vehicle?.modello || ''
        return targa ? `${marca} ${modello} (${targa})` : '-'
      },
    },
    {
      title: 'Date',
      key: 'dates',
      width: 160,
      render: (_, record) => (
        <Space size={0} direction="vertical" style={{ fontSize: '12px' }}>
          <div>Comp: {dayjs(record.data_compilazione).format('DD/MM')}</div>
          {record.data_appuntamento && <div>Appt: {dayjs(record.data_appuntamento).format('DD/MM')}</div>}
          {record.data_fine_prevista && <div>Cons: {dayjs(record.data_fine_prevista).format('DD/MM')}</div>}
        </Space>
      ),
    },
    {
      title: 'Stato',
      dataIndex: 'stato',
      key: 'stato',
      width: 100,
      render: (status) => {
        const statusObj = statuses.find(s => s.value === status)
        return statusObj ? <Tag color={statusObj.color} style={{ fontSize: '11px' }}>{statusObj.label}</Tag> : '-'
      },
    },
    {
      title: 'Costo',
      dataIndex: 'costo_stimato',
      key: 'costo_stimato',
      width: 90,
      render: (cost) => cost ? `€${cost.toLocaleString('it-IT')}` : '-',
    },
    {
      title: 'Azioni',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            title="Modifica"
          />
          <Popconfirm
            title="Eliminare?"
            onConfirm={() => handleDelete(record.id)}
            okText="Sì"
            cancelText="No"
          >
            <Button type="text" size="small" danger icon={<DeleteOutlined />} title="Elimina" />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // LAYOUT #4: Mobile/Tablet - Timeline
  const renderTimelineItem = (wo: WorkOrder) => {
    const statusObj = statuses.find(s => s.value === wo.stato)
    return (
      <Card size="small" style={{ marginBottom: 8 }}>
        <Row justify="space-between" align="middle" style={{ marginBottom: 8 }}>
          <Col>
            <Space>
              <strong>{wo.numero_scheda}</strong>
              <Tag color={statusObj?.color} style={{ fontSize: '11px' }}>
                {statusObj?.label}
              </Tag>
            </Space>
          </Col>
          <Col>
            <small style={{ color: '#999' }}>€{wo.costo_stimato?.toLocaleString('it-IT') || '0'}</small>
          </Col>
        </Row>
        
        <div style={{ marginBottom: 8, fontSize: '13px' }}>
          <Divider style={{ margin: '4px 0' }} />
          <div>{wo.customer_nome || (wo.customer ? `${wo.customer.nome} ${wo.customer.cognome}` : '-')}</div>
          <small style={{ color: '#666' }}>
            {(wo.vehicle_marca || wo.vehicle?.marca) && 
              `${wo.vehicle_marca || wo.vehicle?.marca} ${wo.vehicle_modello || wo.vehicle?.modello}`}
          </small>
        </div>
        
        <Row gutter={8} style={{ fontSize: '12px', marginBottom: 8 }}>
          <Col span={8}>
            <small>📋 Comp: {dayjs(wo.data_compilazione).format('DD/MM')}</small>
          </Col>
          <Col span={8}>
            {wo.data_appuntamento && <small>📅 Appt: {dayjs(wo.data_appuntamento).format('DD/MM')}</small>}
          </Col>
          <Col span={8}>
            <small>✔️ Cons: {wo.data_fine_prevista ? dayjs(wo.data_fine_prevista).format('DD/MM') : '-'}</small>
          </Col>
        </Row>
        
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(wo)}
          >
            Modifica
          </Button>
          <Button
            type="text"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(wo.id)}
          >
            Elimina
          </Button>
        </Space>
      </Card>
    )
  }

  return (
    <div>
      <PageHeader
        title="Schede Lavoro"
        extra={[
          <Select
            key="status-filter"
            placeholder="Filtra per stato"
            style={{ width: 200 }}
            allowClear
            onChange={setStatusFilter}
            options={statuses.map(s => ({ value: s.value, label: s.label }))}
          />,
          <Input.Search
            key="search"
            placeholder="Cerca scheda..."
            onSearch={setSearchText}
            style={{ width: 300 }}
            allowClear
          />,
          <Button
            key="add"
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
            size="large"
          >
            Nuova Scheda Lavoro
          </Button>,
        ]}
      />

      {/* Data Filter Section */}
      <Card style={{ marginBottom: 16, background: '#fafafa' }}>
        <Row gutter={16} align="middle">
          <Col span={8}>
            <Select
              value={dateFilterType}
              onChange={setDateFilterType}
              style={{ width: '100%' }}
              options={[
                { value: 'compilazione', label: '📋 Visualizza per Data Compilazione' },
                { value: 'appuntamento', label: '📅 Visualizza per Data Appuntamento' },
                { value: 'consegna', label: '✔️ Visualizza per Data Consegna Prevista' },
              ]}
            />
          </Col>
          <Col span={8}>
            <DatePicker
              value={dateFilter ? dayjs(dateFilter) : null}
              onChange={(date) => setDateFilter(date?.format('YYYY-MM-DD') || '')}
              format="DD/MM/YYYY"
              placeholder="Seleziona data (opzionale)"
              style={{ width: '100%' }}
            />
          </Col>
          <Col span={8}>
            <Space style={{ width: '100%', justifyContent: 'space-between' }}>
              <Button onClick={() => setDateFilter(dayjs().format('YYYY-MM-DD'))}>
                📅 Oggi
              </Button>
              <Button onClick={() => setDateFilter('')}>
                🔄 Mostra Tutti
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* ERROR DISPLAY */}
      {workOrdersError && (
        <Card style={{ marginBottom: 16, borderColor: '#ff4d4f', backgroundColor: '#fff1f0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: '#ff4d4f', fontWeight: 'bold', marginBottom: '8px' }}>
                ❌ Errore nel caricamento delle schede lavoro
              </p>
              <p style={{ color: '#ff4d4f', fontSize: '12px', marginTop: '8px' }}>
                {workOrdersError instanceof Error ? workOrdersError.message : 'Errore sconosciuto'}
              </p>
            </div>
            <Button 
              danger 
              onClick={() => window.location.reload()}
              style={{ marginLeft: '16px' }}
            >
              🔄 Ricarica
            </Button>
          </div>
        </Card>
      )}

      {/* LAYOUT RESPONSIVO */}
      {isDesktop ? (
        // DESKTOP: Layout #1 - Minimalista Orizzontale (Compact Table)
        <Table
          columns={desktopColumns}
          dataSource={filteredWorkOrders}
          rowKey="id"
          loading={isLoading}
          size="small"
          scroll={{ x: 1000 }}
          pagination={{
            current: page,
            pageSize: 10,
            total: filteredWorkOrders.length,
            onChange: setPage,
            showTotal: (total) => `Totale ${total} schede`,
          }}
          style={{ fontSize: '13px' }}
        />
      ) : (
        // MOBILE/TABLET: Layout #4 - Timeline Cards
        <div>
          {isLoading ? (
            <Card loading />
          ) : filteredWorkOrders.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {filteredWorkOrders.map((wo) => renderTimelineItem(wo))}
            </div>
          ) : (
            <Card style={{ textAlign: 'center', padding: '40px 20px' }}>
              <p style={{ color: '#999' }}>Nessuna scheda lavoro trovata</p>
            </Card>
          )}
          {filteredWorkOrders.length > 0 && (
            <div style={{ textAlign: 'center', marginTop: 16, fontSize: '12px', color: '#666' }}>
              Totale: {filteredWorkOrders.length} schede
            </div>
          )}
        </div>
      )}

      {/* MAIN WORK ORDER MODAL */}
      <Modal
        title={editingWorkOrder ? 'Modifica Scheda' : 'Nuova Scheda'}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false)
          form.resetFields()
          setSelectedCustomerId(undefined)
          setFormInterventions([])
        }}
        onOk={() => form.submit()}
        confirmLoading={createWorkOrderMutation.isPending || updateWorkOrderMutation.isPending}
        width={screens.md ? 1000 : '95vw'}
        className="compact-modal"
        centered
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          className="compact-form"
        >
          {/* SEZIONE: Cliente e Veicolo */}
          <div className="form-section">
            <div className="form-section-title">
              <UserAddOutlined /> Cliente e Veicolo
            </div>
            <div className="form-grid form-grid-2">
              <Form.Item label="Cliente" required style={{ marginBottom: 0 }}>
                <div className="field-with-btn">
                  <Form.Item
                    name="customer_id"
                    noStyle
                    rules={[{ required: true, message: 'Seleziona cliente' }]}
                  >
                    <Select
                      showSearch
                      placeholder="Seleziona cliente"
                      optionFilterProp="children"
                      onChange={handleCustomerChange}
                      filterOption={(input, option) =>
                        (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                      }
                      options={customersData?.items.map(c => ({
                        value: c.id,
                        label: `${c.nome} ${c.cognome}`,
                      }))}
                    />
                  </Form.Item>
                  <Button
                    type="primary"
                    icon={<UserAddOutlined />}
                    onClick={handleQuickAddCustomer}
                    title="Nuovo cliente"
                  />
                </div>
              </Form.Item>

              <Form.Item label="Veicolo" required style={{ marginBottom: 0 }}>
                <div className="field-with-btn">
                  <Form.Item
                    name="vehicle_id"
                    noStyle
                    rules={[{ required: true, message: 'Seleziona veicolo' }]}
                  >
                    <Select
                      showSearch
                      placeholder={selectedCustomerId ? "Seleziona veicolo" : "Prima il cliente"}
                      disabled={!selectedCustomerId}
                      optionFilterProp="children"
                      filterOption={(input, option) =>
                        (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                      }
                      options={customerVehicles?.map(v => ({
                        value: v.id,
                        label: `${v.targa} - ${v.marca} ${v.modello}`,
                      }))}
                    />
                  </Form.Item>
                  <Button
                    type="primary"
                    icon={<CarOutlined />}
                    onClick={handleQuickAddVehicle}
                    disabled={!selectedCustomerId}
                    title="Nuovo veicolo"
                  />
                </div>
              </Form.Item>
            </div>
          </div>

          {/* SEZIONE: Dettagli */}
          <div className="form-section">
            <div className="form-section-title">
              <FileTextOutlined /> Dettagli Scheda
            </div>
            <div className="form-grid form-grid-4">
              <Form.Item name="numero_scheda" label="N. Scheda">
                <Input disabled placeholder="Auto" size="small" />
              </Form.Item>
              
              <Form.Item name="stato" label="Stato" rules={[{ required: true }]}>
                <Select size="small" options={statuses.map(s => ({ value: s.value, label: s.label }))} />
              </Form.Item>
              
              <Form.Item name="priorita" label="Priorità" initialValue={priorityTypes?.[0]?.nome || "media"}>
                <Select size="small" placeholder="Priorità">
                  {priorityTypes?.filter(p => p.attivo).map(priority => (
                    <Select.Option key={priority.id} value={priority.nome}>
                      {priority.nome}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                name="costo_stimato"
                label="Costo €"
              >
                <InputNumber min={0} step={0.01} style={{ width: '100%' }} size="small" />
              </Form.Item>
            </div>

            <div className="form-grid form-grid-3">
              <Form.Item
                name="data_compilazione"
                label="Data Compilazione"
                rules={[{ required: true }]}
                getValueProps={(value) => ({ value: value ? dayjs(value) : undefined })}
                normalize={(value) => value?.format ? value.format('YYYY-MM-DD') : value}
              >
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" size="small" />
              </Form.Item>

              <Form.Item
                name="data_appuntamento"
                label="Appuntamento"
                getValueProps={(value) => ({ value: value ? dayjs(value) : undefined })}
                normalize={(value) => value?.format ? value.format('YYYY-MM-DD') : value}
              >
                <div className="field-with-btn">
                  <Input 
                    placeholder="Nessuna data"
                    readOnly
                    value={displayedAppointmentDate}
                    size="small"
                  />
                  <Button
                    type="primary"
                    icon={<CalendarOutlined />}
                    onClick={() => setIsCalendarModalOpen(true)}
                    size="small"
                  />
                </div>
              </Form.Item>

              <Form.Item
                name="data_fine_prevista"
                label="Consegna Prevista"
                getValueProps={(value) => ({ value: value ? dayjs(value) : undefined })}
                normalize={(value) => value?.format ? value.format('YYYY-MM-DD') : value}
              >
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" size="small" />
              </Form.Item>
            </div>
          </div>

          {/* SEZIONE: Interventi */}
          <div className="form-section">
            <div className="section-header">
              <span className="section-header-title">🔧 Interventi</span>
              <Button 
                type="primary" 
                size="small"
                className="btn-add-intervention"
                onClick={() => {
                  const newIntervention: any = {
                    progressivo: (formInterventions.filter(i => i.progressivo).length > 0 ? Math.max(...formInterventions.filter(i => i.progressivo).map(i => i.progressivo!)) : 0) + 1,
                    descrizione_intervento: '',
                    durata_stimata: 0,
                    tipo_intervento: 'Meccanico',
                    _isNew: true
                  }
                  setFormInterventions([...formInterventions, newIntervention])
                }}
              >
                <PlusOutlined /> Aggiungi
              </Button>
            </div>
            
            {formInterventions.length === 0 ? (
              <div className="interventions-empty">
                Nessun intervento. Clicca "Aggiungi" per iniziare.
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="interventions-table">
                  <colgroup>
                    <col style={{ width: '5%' }} />
                    <col style={{ width: '60%' }} />
                    <col style={{ width: '10%' }} />
                    <col style={{ width: '15%' }} />
                    <col style={{ width: '10%' }} />
                  </colgroup>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Descrizione</th>
                      <th>Ore</th>
                      <th>Tipo</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {formInterventions.map((intervention, idx) => (
                      <tr key={`intervention-${idx}-${intervention.id || 'new'}`}>
                        <td style={{ textAlign: 'center', paddingTop: 6, paddingBottom: 6 }}>{intervention.progressivo}</td>
                        <td style={{ paddingTop: 4, paddingBottom: 4 }}>
                          <Input
                            value={intervention.descrizione_intervento}
                            onChange={(e) => {
                              const updated = [...formInterventions]
                              updated[idx].descrizione_intervento = e.target.value
                              updated[idx]._modified = true
                              setFormInterventions(updated)
                            }}
                            placeholder="Descrizione intervento"
                            size="small"
                          />
                        </td>
                        <td style={{ textAlign: 'center', paddingTop: 4, paddingBottom: 4 }}>
                          <InputNumber
                            value={intervention.durata_stimata}
                            onChange={(value) => {
                              const updated = [...formInterventions]
                              updated[idx].durata_stimata = value || 0
                              updated[idx]._modified = true
                              setFormInterventions(updated)
                            }}
                            min={0}
                            max={100}
                            step={0.5}
                            style={{ width: '100%' }}
                            size="small"
                          />
                        </td>
                        <td style={{ textAlign: 'center', paddingTop: 4, paddingBottom: 4 }}>
                          <Select
                            value={intervention.tipo_intervento}
                            onChange={(value) => {
                              const updated = [...formInterventions]
                              updated[idx].tipo_intervento = value as 'Meccanico' | 'Carrozziere'
                              updated[idx]._modified = true
                              setFormInterventions(updated)
                            }}
                            style={{ width: '100%' }}
                            size="small"
                          >
                            <Select.Option value="Meccanico">Mecc.</Select.Option>
                            <Select.Option value="Carrozziere">Carr.</Select.Option>
                          </Select>
                        </td>
                        <td style={{ textAlign: 'center', paddingTop: 6, paddingBottom: 6 }}>
                          <Button
                            type="text"
                            danger
                            size="small"
                            onClick={() => setFormInterventions(formInterventions.filter((_, i) => i !== idx))}
                          >
                            <DeleteOutlined />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* SEZIONE: Descrizione Danno */}
          <div className="form-section">
            <div className="form-section-title">
              📝 Descrizione Danno
            </div>
            <Form.Item
              name="valutazione_danno"
              label="Descrizione Danno"
              rules={[{ required: true, message: 'Inserisci descrizione' }]}
            >
              <VoiceTextarea
                placeholder="Clicca il microfono e descrivi a voce il danno... oppure digita manualmente"
                rows={3}
                minHeight={150}
                maxHeight={300}
                classNamePrefix="descrizione-danno"
                label="Descrizione Danno"
                debugPrefix="DescrizioneDanno"
              />
            </Form.Item>

            <Form.Item name="note" label="Note">
              <VoiceTextarea
                placeholder="Aggiungi note... oppure clicca il microfono per dettare"
                rows={1}
                minHeight={60}
                maxHeight={150}
                classNamePrefix="notes"
                label="Note"
                debugPrefix="Notes"
              />
            </Form.Item>
          </div>

          {/* State Transition */}
          {editingWorkOrder && (
            <WorkOrderStateTransition
              workOrderId={editingWorkOrder.id}
              currentState={editingWorkOrder.stato}
              interventionsCount={formInterventions.length}
              hasDescrizione={!!form.getFieldValue('descrizione')}
              onStateChange={(newState) => {
                // Aggiorna lo stato locale
                setEditingWorkOrder({
                  ...editingWorkOrder,
                  stato: newState as WorkOrderStatus
                })
                // Aggiorna anche il form per sincronizzare la UI
                form.setFieldsValue({ stato: newState })
                // Invalida la cache per ricaricare i dati dal server
                queryClient.invalidateQueries({ queryKey: ['work-orders'] })
              }}
            />
          )}
        </Form>
      </Modal>

      {/* QUICK ADD CUSTOMER MODAL */}
      <Modal
        title={<Space><UserAddOutlined /> Crea Nuovo Cliente</Space>}
        open={isCustomerModalOpen}
        onCancel={() => {
          setIsCustomerModalOpen(false)
          customerForm.resetFields()
        }}
        onOk={() => customerForm.submit()}
        confirmLoading={createCustomerMutation.isPending}
        width={700}
      >
        <Form
          form={customerForm}
          layout="vertical"
          onFinish={handleCustomerSubmit}
          initialValues={{ tipo: 'privato' }}
        >
          <Form.Item
            name="tipo"
            label="Tipo Cliente"
            rules={[{ required: true, message: 'Seleziona il tipo' }]}
          >
            <Select>
              {customerTypes?.filter(ct => ct.attivo).map(customerType => (
                <Select.Option key={customerType.id} value={customerType.nome.toLowerCase()}>
                  {customerType.nome}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="nome"
                label="Nome"
                rules={[{ required: true, message: 'Inserisci il nome' }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="cognome"
                label="Cognome"
                rules={[{ required: true, message: 'Inserisci il cognome' }]}
              >
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="email" label="Email">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="cellulare" label="Cellulare">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item 
            name="codice_fiscale" 
            label="Codice Fiscale"
            tooltip="Opzionale ma consigliato"
          >
            <Input placeholder="Es. RSSMRA80A01H501U" />
          </Form.Item>
        </Form>
      </Modal>

      {/* QUICK ADD VEHICLE MODAL */}
      <Modal
        title={<Space><CarOutlined /> Crea Nuovo Veicolo</Space>}
        open={isVehicleModalOpen}
        onCancel={() => {
          setIsVehicleModalOpen(false)
          vehicleForm.resetFields()
        }}
        onOk={() => vehicleForm.submit()}
        confirmLoading={createVehicleMutation.isPending}
        width={700}
      >
        <Form
          form={vehicleForm}
          layout="vertical"
          onFinish={handleVehicleSubmit}
        >
          <Form.Item name="customer_id" hidden>
            <Input />
          </Form.Item>

          <Form.Item
            name="targa"
            label="Targa"
            rules={[{ required: true, message: 'Inserisci la targa' }]}
          >
            <Input placeholder="XX000XX" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="marca"
                label="Marca"
                rules={[{ required: true, message: 'Inserisci la marca' }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="modello"
                label="Modello"
                rules={[{ required: true, message: 'Inserisci il modello' }]}
              >
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="anno" 
                label="Anno"
                rules={[{ required: true, message: 'Inserisci l\'anno' }]}
              >
                <InputNumber min={1900} max={new Date().getFullYear() + 1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="colore" label="Colore">
                <Input placeholder="Colore veicolo" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="telaio" label="Numero Telaio (opzionale)">
            <Input placeholder="17 caratteri VIN" />
          </Form.Item>
        </Form>
      </Modal>

      {/* CALENDAR MODAL FOR GOOGLE CALENDAR BOOKING */}
      {isCalendarModalOpen && (
        <CalendarModal
          onConfirm={handleCalendarConfirm}
          onCancel={() => setIsCalendarModalOpen(false)}
          returnUrl={editingWorkOrder?.id ? `/work-orders?id=${editingWorkOrder.id}` : undefined}
          currentAppointmentDate={editingWorkOrder?.data_appuntamento}
          currentCustomerId={editingWorkOrder?.customer_id}
          customerName={
            editingWorkOrder?.customer_nome || 
            (editingWorkOrder?.customer ? `${editingWorkOrder.customer.nome} ${editingWorkOrder.customer.cognome}` : undefined)
          }
        />
      )}
    </div>
  )
}

export default WorkOrdersPage
