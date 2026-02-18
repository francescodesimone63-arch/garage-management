import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, Select, Space, Tag, Popconfirm, message, InputNumber, Row, Col, Divider, Upload, Spin, DatePicker, Card } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, CarOutlined, DownloadOutlined, UploadOutlined, FileOutlined } from '@ant-design/icons'
import type { ColumnsType, TableProps } from 'antd/es/table'
import type { UploadFile } from 'antd/es/upload/interface'
import dayjs from 'dayjs'
import PageHeader from '@/components/PageHeader'
import { useCourtesyCars, useCreateCourtesyCar, useUpdateCourtesyCar, useDeleteCourtesyCar, useUploadContratto } from '@/hooks/useCourtesyCars'
import { useVehicles } from '@/hooks/useVehicles'
import type { CourtesyCar, Vehicle } from '@/types'

const CourtesyCarsPage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCourtesyCar, setEditingCourtesyCar] = useState<CourtesyCar | null>(null)
  const [form] = Form.useForm()
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const { data, isLoading, refetch } = useCourtesyCars()
  const { data: vehiclesData, refetch: refetchVehicles } = useVehicles(1, 10000)
  const createMutation = useCreateCourtesyCar()
  const updateMutation = useUpdateCourtesyCar()
  const deleteMutation = useDeleteCourtesyCar()
  const uploadMutation = useUploadContratto(editingCourtesyCar?.id || 0)

  // Filtra veicoli che sono "auto di cortesia"
  const courtesyVehicles = vehiclesData?.items?.filter(v => v.courtesy_car === true) || []

  // Ricarica i dati dei veicoli quando la pagina diventa visibile (per sincronizzare la disponibilità)
  useEffect(() => {
    // Ricarica i veicoli ogni 2 secondi per riflettere i cambiamenti di disponibilità in tempo reale
    const interval = setInterval(() => {
      refetchVehicles()
    }, 2000)
    return () => clearInterval(interval)
  }, [refetchVehicles])

  const handleCreate = () => {
    setEditingCourtesyCar(null)
    form.resetFields()
    setFileList([])
    setIsModalOpen(true)
  }

  const handleEdit = (record: CourtesyCar) => {
    setEditingCourtesyCar(record)
    form.setFieldsValue(record)
    // Se ha un file, mostra nel upload
    if (record.contratto_firmato) {
      setFileList([
        {
          uid: '-1',
          name: 'contratto.pdf',
          status: 'done',
          url: `/api/v1/courtesy-cars/${record.id}/contratto/download`,
        },
      ])
    } else {
      setFileList([])
    }
    setIsModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    await deleteMutation.mutateAsync(id)
    refetch()
  }

  const handleSubmit = async (values: any) => {
    try {
      setIsUploading(true)
      
      let createdOrUpdatedRecord: any
      
      if (editingCourtesyCar) {
        await updateMutation.mutateAsync({
          id: editingCourtesyCar.id,
          data: values,
        })
        createdOrUpdatedRecord = editingCourtesyCar
      } else {
        createdOrUpdatedRecord = await createMutation.mutateAsync(values)
      }

      // Upload del file PDF se presente e nuovo
      if (fileList.length > 0 && fileList[0].originFileObj) {
        const newFile = fileList[0].originFileObj as File
        
        // Attendi 500ms per assicurarti che il record sia stato salvato
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Carica il file
        await uploadMutation.mutateAsync(newFile)
        message.success('Contratto caricato con successo!')
      }

      setIsModalOpen(false)
      form.resetFields()
      setFileList([])
      refetch()
    } catch (error: any) {
      console.error('Errore:', error)
      message.error(error?.message || 'Errore durante il salvataggio')
    } finally {
      setIsUploading(false)
    }
  }

  // Mapping stato con colori
  const getStatusTag = (status: string) => {
    const statusColors: Record<string, string> = {
      disponibile: 'green',
      assegnata: 'blue',
      manutenzione: 'orange',
      fuori_servizio: 'red',
    }
    const statusLabels: Record<string, string> = {
      disponibile: '✅ Disponibile',
      assegnata: '🏍️ Assegnata',
      manutenzione: '🔧 Manutenzione',
      fuori_servizio: '🚫 Fuori Servizio',
    }
    return (
      <Tag color={statusColors[status] || 'default'}>
        {statusLabels[status] || status}
      </Tag>
    )
  }

  // Ottieni nome veicolo dal vehicle_id
  const getVehicleName = (vehicleId: number) => {
    const vehicle = courtesyVehicles.find(v => v.id === vehicleId)
    if (!vehicle) return '-'
    return `${vehicle.targa} - ${vehicle.marca} ${vehicle.modello}`
  }

  const columns: ColumnsType<CourtesyCar> = [
    {
      title: 'Veicolo',
      key: 'vehicle',
      render: (_, record) => (
        <Space>
          <CarOutlined />
          <strong>{getVehicleName(record.vehicle_id)}</strong>
        </Space>
      ),
    },
    {
      title: 'Tipo Contratto',
      dataIndex: 'contratto_tipo',
      key: 'contratto_tipo',
      render: (tipo) => (
        <Tag color={tipo === 'leasing' ? 'blue' : tipo === 'affitto' ? 'green' : 'default'}>
          {tipo?.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Fornitore',
      dataIndex: 'fornitore_contratto',
      key: 'fornitore_contratto',
      render: (fornitore) => fornitore || '-',
    },
    {
      title: 'Disponibilità',
      key: 'disponibile',
      render: (_, record) => {
        const vehicle = courtesyVehicles.find(v => v.id === record.vehicle_id)
        const isAvailable = vehicle?.disponibile ?? true
        return (
          <Tag color={isAvailable ? 'green' : 'red'}>
            {isAvailable ? '✅ Disponibile' : '❌ Assegnata'}
          </Tag>
        )
      },
    },
    {
      title: 'Canone Mensile',
      dataIndex: 'canone_mensile',
      key: 'canone_mensile',
      render: (canone) => canone ? `€ ${parseFloat(canone).toLocaleString('it-IT')}` : '-',
    },
    {
      title: 'Scadenza',
      dataIndex: 'data_scadenza_contratto',
      key: 'data_scadenza_contratto',
      render: (date) => date ? dayjs(date).format('DD/MM/YYYY') : '-',
    },
    {
      title: 'Contratto',
      dataIndex: 'contratto_firmato',
      key: 'contratto_firmato',
      render: (contratto, record) => (
        contratto ? (
          <Button
            type="link"
            icon={<DownloadOutlined />}
            href={`/api/v1/courtesy-cars/${record.id}/contratto/download`}
            target="_blank"
          >
            Scarica
          </Button>
        ) : (
          <span style={{ color: '#999' }}>Nessun file</span>
        )
      ),
    },
    {
      title: 'Azioni',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Modifica
          </Button>
          <Popconfirm
            title="Sei sicuro di voler eliminare questa auto di cortesia?"
            onConfirm={() => handleDelete(record.id)}
            okText="Sì"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Elimina
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Gestione Auto di Cortesia"
        extra={[
          <Button
            key="add"
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            Nuovo Contratto
          </Button>,
        ]}
      />

      {courtesyVehicles.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ marginBottom: '16px', fontSize: '32px' }}>🚗</div>
          <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>
            Nessuna auto di cortesia disponibile
          </div>
          <div style={{ fontSize: '14px', color: '#999' }}>
            Prima flagga un veicolo come "Auto di Cortesia" nella sezione Gestione Veicoli
          </div>
        </Card>
      ) : (
        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showTotal: (total) => `Totale ${total} contratti`,
          }}
        />
      )}

      {/* MODAL */}
      <Modal
        title={editingCourtesyCar ? 'Modifica Auto di Cortesia' : 'Nuovo Contratto Auto di Cortesia'}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false)
          form.resetFields()
          setFileList([])
        }}
        onOk={() => form.submit()}
        width={800}
        confirmLoading={isUploading || createMutation.isPending || updateMutation.isPending}
        okButtonProps={{ disabled: isUploading || createMutation.isPending || updateMutation.isPending }}
      >
        {/* Intestazione veicolo */}
        {editingCourtesyCar && (
          <Card style={{ marginBottom: '16px', backgroundColor: '#f5f5f5' }}>
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ fontSize: '12px', color: '#999' }}>VEICOLO</div>
                <div style={{ fontSize: '14px', fontWeight: 'bold', marginTop: '4px' }}>
                  {getVehicleName(editingCourtesyCar.vehicle_id)}
                </div>
              </Col>
              <Col span={12}>
                <div style={{ fontSize: '12px', color: '#999' }}>STATO ATTUALE</div>
                <div style={{ marginTop: '4px' }}>
                  {getStatusTag(editingCourtesyCar.stato)}
                </div>
              </Col>
            </Row>
          </Card>
        )}

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          {!editingCourtesyCar && (
            <Form.Item
              name="vehicle_id"
              label="Veicolo"
              rules={[{ required: true, message: 'Seleziona un veicolo' }]}
            >
              <Select
                placeholder="Seleziona auto di cortesia"
                options={courtesyVehicles.map(v => ({
                  value: v.id,
                  label: `${v.targa} - ${v.marca} ${v.modello} (${v.anno})`,
                }))}
              />
            </Form.Item>
          )}

          <Divider orientation="left">Dati Contrattuali</Divider>

          <Form.Item
            name="contratto_tipo"
            label="Tipo di Contratto"
            rules={[{ required: true, message: 'Seleziona il tipo' }]}
          >
            <Select
              placeholder="Leasing / Affitto / Proprietà"
              options={[
                { label: '📋 Leasing', value: 'leasing' },
                { label: '🏠 Affitto', value: 'affitto' },
                { label: '🔑 Proprietà Tiber Car', value: 'proprieta' },
              ]}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="fornitore_contratto"
                label="Fornitore/Società"
              >
                <Input placeholder="Leasing company, etc." maxLength={200} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="stato"
                label="Stato Auto"
              >
                <Select
                  placeholder="Stato"
                  options={[
                    { label: '✅ Disponibile', value: 'disponibile' },
                    { label: '🏍️ Assegnata', value: 'assegnata' },
                    { label: '🔧 Manutenzione', value: 'manutenzione' },
                    { label: '🚫 Fuori Servizio', value: 'fuori_servizio' },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="data_inizio_contratto"
                label="Data Inizio Contratto"
              >
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="data_scadenza_contratto"
                label="Data Scadenza Contratto"
              >
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="canone_mensile"
                label="Canone Mensile (€)"
              >
                <InputNumber min={0} step={0.01} style={{ width: '100%' }} placeholder="1.000,00" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="km_inclusi_anno"
                label="KM Inclusi per Anno"
              >
                <InputNumber min={0} style={{ width: '100%' }} placeholder="15.000" />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">Documenti</Divider>

          <Form.Item
            name="contratto_firmato"
            label="Contratto Firmato (PDF)"
          >
            <Upload
              accept=".pdf"
              maxCount={1}
              fileList={fileList}
              onChange={({ fileList: newFileList }) => setFileList(newFileList)}
            >
              <Button icon={<UploadOutlined />}>Carica PDF</Button>
            </Upload>
          </Form.Item>

          <Divider orientation="left">Note</Divider>

          <Form.Item
            name="note"
            label="Note"
          >
            <Input.TextArea rows={3} placeholder="Note aggiuntive..."  />
          </Form.Item>

          {/* Campi di sistema (visualizzazione sola lettura) */}
          {editingCourtesyCar && (
            <>
              <Divider orientation="left">Informazioni di Sistema</Divider>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="Creato il">
                    <div>{dayjs(editingCourtesyCar.created_at).format('DD/MM/YYYY HH:mm')}</div>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Modificato il">
                    <div>{dayjs(editingCourtesyCar.updated_at).format('DD/MM/YYYY HH:mm')}</div>
                  </Form.Item>
                </Col>
              </Row>
            </>
          )}
        </Form>
      </Modal>
    </div>
  )
}

export default CourtesyCarsPage
