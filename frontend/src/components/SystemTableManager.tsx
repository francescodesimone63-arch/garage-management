import { Table, Button, Space, message, Modal, Form, Input, Popconfirm } from 'antd'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useState, useEffect } from 'react'
import axiosInstance from '@/lib/axios'

interface SystemTableItem {
  id: number
  nome: string
  descrizione?: string
  attivo: boolean
  created_at?: string
  updated_at?: string
}

interface SystemTableProps {
  title: string
  endpoint: string
  columns: ColumnsType<SystemTableItem>
  onLoadData?: (data: SystemTableItem[]) => void
}

export const SystemTableManager = ({ title, endpoint, columns: customColumns, onLoadData }: SystemTableProps) => {
  const [data, setData] = useState<SystemTableItem[]>([])
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<SystemTableItem | null>(null)
  const [form] = Form.useForm()

  // Load data
  const loadData = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get<SystemTableItem[]>(endpoint)
      console.log('✅ Dati caricati da:', endpoint, response.data)
      setData(response.data)
      onLoadData?.(response.data)
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
        await axiosInstance.put(`${endpoint}/${editingItem.id}`, values)
        message.success('Record aggiornato con successo')
      } else {
        await axiosInstance.post(endpoint, values)
        message.success('Record creato con successo')
      }
      setIsModalOpen(false)
      setEditingItem(null)
      form.resetFields()
      loadData()
    } catch (error: any) {
      console.error('Errore:', error)
      message.error(error.response?.data?.detail || 'Errore durante il salvataggio')
    }
  }

  // Delete
  const handleDelete = async (id: number) => {
    try {
      await axiosInstance.delete(`${endpoint}/${id}`)
      message.success('Record eliminato con successo')
      loadData()
    } catch (error: any) {
      console.error('Errore:', error)
      message.error(error.response?.data?.detail || 'Errore durante l\'eliminazione')
    }
  }

  // Edit
  const handleEdit = (record: SystemTableItem) => {
    setEditingItem(record)
    form.setFieldsValue({
      nome: record.nome,
      descrizione: record.descrizione,
      attivo: record.attivo,
    })
    setIsModalOpen(true)
  }

  // New
  const handleNew = () => {
    setEditingItem(null)
    form.resetFields()
    setIsModalOpen(true)
  }

  // Columns with action column
  const actionColumn: ColumnsType<SystemTableItem> = [
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
            description="Sei sicuro di voler eliminare questo record?"
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

  const finalColumns = [...customColumns, ...actionColumn]

  return (
    <>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleNew}>
          Aggiungi {title}
        </Button>
      </div>

      <Table
        columns={finalColumns}
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
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item
            name="nome"
            label="Nome"
            rules={[{ required: true, message: 'Nome obbligatorio' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="descrizione" label="Descrizione">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
