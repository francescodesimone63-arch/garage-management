import { Table, Button, Space, message, Modal, Form, Input, Popconfirm, Checkbox } from 'antd'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useState, useEffect } from 'react'
import axiosInstance from '@/lib/axios'

interface InterventionStatusType {
  id: number
  codice: string
  nome: string
  descrizione?: string
  richiede_nota: boolean
  attivo: boolean
  ordine: number
  created_at?: string
  updated_at?: string
}

interface InterventionStatusTypeManagerProps {
  title: string
  endpoint: string
}

export const InterventionStatusTypeManager = ({ title, endpoint }: InterventionStatusTypeManagerProps) => {
  const [data, setData] = useState<InterventionStatusType[]>([])
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<InterventionStatusType | null>(null)
  const [form] = Form.useForm()

  // Load data
  const loadData = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get<InterventionStatusType[]>(endpoint)
      console.log('✅ Dati caricati da:', endpoint, response.data)
      setData(response.data)
    } catch (error: any) {
      console.error('❌ Errore caricamento dati da', endpoint, ':', error)
      console.error('📋 Dettagli errore:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        message: error.message
      })
      message.error(`Errore nel caricamento dei dati: ${error.response?.status || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [endpoint])

  // Create or update
  const handleSave = async (values: any) => {
    try {
      if (editingItem) {
        console.log('🔄 Aggiornamento:', { id: editingItem.id, values })
        await axiosInstance.put(`${endpoint}/${editingItem.id}`, values)
        message.success('Stato intervento aggiornato con successo')
      } else {
        console.log('✨ Creazione:', values)
        await axiosInstance.post(endpoint, values)
        message.success('Stato intervento creato con successo')
      }
      setIsModalOpen(false)
      setEditingItem(null)
      form.resetFields()
      loadData()
    } catch (error: any) {
      console.error('❌ Errore salvataggio:', error)
      console.error('📋 Response data:', error.response?.data)
      message.error(error.response?.data?.detail || 'Errore durante il salvataggio')
    }
  }

  // Delete
  const handleDelete = async (id: number) => {
    try {
      await axiosInstance.delete(`${endpoint}/${id}`)
      message.success('Stato intervento eliminato con successo')
      loadData()
    } catch (error: any) {
      console.error('Errore:', error)
      message.error(error.response?.data?.detail || 'Errore durante l\'eliminazione')
    }
  }

  // Edit
  const handleEdit = (record: InterventionStatusType) => {
    setEditingItem(record)
    form.setFieldsValue({
      codice: record.codice,
      nome: record.nome,
      descrizione: record.descrizione,
      richiede_nota: record.richiede_nota,
      attivo: record.attivo,
      ordine: record.ordine,
    })
    setIsModalOpen(true)
  }

  // New
  const handleNew = () => {
    setEditingItem(null)
    form.resetFields()
    form.setFieldsValue({
      richiede_nota: false,
      attivo: true,
      ordine: 0,
    })
    setIsModalOpen(true)
  }

  const columns: ColumnsType<InterventionStatusType> = [
    {
      title: 'Codice',
      dataIndex: 'codice',
      key: 'codice',
      width: 130,
    },
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      width: 150,
    },
    {
      title: 'Descrizione',
      dataIndex: 'descrizione',
      key: 'descrizione',
      ellipsis: true,
    },
    {
      title: 'Richiede Nota',
      dataIndex: 'richiede_nota',
      key: 'richiede_nota',
      width: 110,
      render: (richiede: boolean) => richiede ? '✅' : '❌'
    },
    {
      title: 'Ordine',
      dataIndex: 'ordine',
      key: 'ordine',
      width: 80,
    },
    {
      title: 'Attivo',
      dataIndex: 'attivo',
      key: 'attivo',
      width: 80,
      render: (attivo: boolean) => attivo ? '✅' : '❌'
    },
    {
      title: 'Azioni',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          />
          <Popconfirm
            title="Elimina"
            description="Sei sicuro di voler eliminare questo stato?"
            onConfirm={() => handleDelete(record.id)}
            okText="Si"
            cancelText="No"
          >
            <Button danger size="small" icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleNew}>
          Aggiungi {title}
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        loading={loading}
        rowKey="id"
        pagination={{ pageSize: 10 }}
        size="small"
      />

      <Modal
        title={editingItem ? `Modifica ${title}` : `Aggiungi ${title}`}
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => {
          setIsModalOpen(false)
          setEditingItem(null)
          form.resetFields()
        }}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item
            name="codice"
            label="Codice"
            rules={[{ required: true, message: 'Codice obbligatorio (es: preso_in_carico)' }]}
          >
            <Input placeholder="es: preso_in_carico" />
          </Form.Item>

          <Form.Item
            name="nome"
            label="Nome"
            rules={[{ required: true, message: 'Nome obbligatorio' }]}
          >
            <Input placeholder="es: Preso in carico" />
          </Form.Item>

          <Form.Item name="descrizione" label="Descrizione">
            <Input.TextArea rows={3} />
          </Form.Item>

          <Form.Item
            name="ordine"
            label="Ordine di visualizzazione"
          >
            <Input type="number" />
          </Form.Item>

          <Form.Item name="richiede_nota" valuePropName="checked">
            <Checkbox>Richiede nota (es: per stato sospeso)</Checkbox>
          </Form.Item>

          <Form.Item name="attivo" valuePropName="checked">
            <Checkbox>Attivo</Checkbox>
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
