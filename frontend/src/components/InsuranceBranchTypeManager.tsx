import { Table, Button, Space, message, Modal, Form, Input, Popconfirm, Switch } from 'antd'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useState, useEffect } from 'react'
import axiosInstance from '@/lib/axios'

interface InsuranceBranchType {
  id: number
  nome: string
  codice: string
  descrizione?: string
  attivo: boolean
  created_at?: string
  updated_at?: string
}

interface InsuranceBranchTypeManagerProps {
  title: string
  endpoint: string
}

export const InsuranceBranchTypeManager = ({ title, endpoint }: InsuranceBranchTypeManagerProps) => {
  const [data, setData] = useState<InsuranceBranchType[]>([])
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<InsuranceBranchType | null>(null)
  const [form] = Form.useForm()

  // Load data
  const loadData = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get<InsuranceBranchType[]>(endpoint)
      console.log('✅ Dati caricati da:', endpoint, response.data)
      setData(response.data)
    } catch (error: any) {
      console.error('❌ Errore caricamento dati da', endpoint, ':', error)
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
  const handleEdit = (record: InsuranceBranchType) => {
    setEditingItem(record)
    form.setFieldsValue({
      nome: record.nome,
      codice: record.codice,
      descrizione: record.descrizione,
      attivo: record.attivo,
    })
    setIsModalOpen(true)
  }

  // New
  const handleNew = () => {
    setEditingItem(null)
    form.resetFields()
    form.setFieldsValue({ attivo: true })
    setIsModalOpen(true)
  }

  // Columns
  const columns: ColumnsType<InsuranceBranchType> = [
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      width: 200,
      sorter: (a, b) => a.nome.localeCompare(b.nome),
    },
    {
      title: 'Codice',
      dataIndex: 'codice',
      key: 'codice',
      width: 120,
    },
    {
      title: 'Descrizione',
      dataIndex: 'descrizione',
      key: 'descrizione',
      ellipsis: true,
    },
    {
      title: 'Attivo',
      dataIndex: 'attivo',
      key: 'attivo',
      width: 80,
      render: (attivo: boolean) => attivo ? '✅' : '❌',
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
        width={500}
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item
            name="nome"
            label="Nome"
            rules={[{ required: true, message: 'Nome obbligatorio' }]}
          >
            <Input placeholder="Es: Responsabilità Civile" />
          </Form.Item>

          <Form.Item
            name="codice"
            label="Codice"
            rules={[{ required: true, message: 'Codice obbligatorio' }]}
          >
            <Input placeholder="Es: rc" />
          </Form.Item>

          <Form.Item name="descrizione" label="Descrizione">
            <Input.TextArea rows={3} placeholder="Descrizione della copertura..." />
          </Form.Item>

          <Form.Item name="attivo" label="Attivo" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
