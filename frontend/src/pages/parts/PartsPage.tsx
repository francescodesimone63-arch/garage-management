import { useState } from 'react'
import { Table, Button, Modal, Form, Input, Space, Tag, Popconfirm, message, InputNumber } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ToolOutlined, WarningOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import PageHeader from '@/components/PageHeader'
import { useParts, useCreatePart, useUpdatePart, useDeletePart } from '@/hooks/useParts'
import type { Part } from '@/types'

const PartsPage = () => {
  const [page, setPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPart, setEditingPart] = useState<Part | null>(null)
  const [form] = Form.useForm()

  const { data, isLoading } = useParts(page, 10, searchText)
  const createMutation = useCreatePart()
  const updateMutation = useUpdatePart()
  const deleteMutation = useDeletePart()

  const handleCreate = () => {
    setEditingPart(null)
    form.resetFields()
    setIsModalOpen(true)
  }

  const handleEdit = (record: Part) => {
    setEditingPart(record)
    form.setFieldsValue(record)
    setIsModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    await deleteMutation.mutateAsync(id)
  }

  const handleSubmit = async (values: any) => {
    try {
      if (editingPart) {
        await updateMutation.mutateAsync({ id: editingPart.id, data: values })
      } else {
        await createMutation.mutateAsync(values)
      }
      setIsModalOpen(false)
      form.resetFields()
    } catch (error) {
      message.error('Errore durante il salvataggio')
    }
  }

  const columns: ColumnsType<Part> = [
    {
      title: 'Codice',
      dataIndex: 'codice',
      key: 'codice',
      render: (text) => (
        <Space>
          <ToolOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
    },
    {
      title: 'Categoria',
      dataIndex: 'categoria',
      key: 'categoria',
      render: (categoria) => categoria ? <Tag>{categoria}</Tag> : '-',
    },
    {
      title: 'Fornitore',
      dataIndex: 'fornitore',
      key: 'fornitore',
      render: (fornitore) => fornitore || '-',
    },
    {
      title: 'Prezzo Vendita',
      dataIndex: 'prezzo_vendita',
      key: 'prezzo_vendita',
      render: (price) => `€ ${(price || 0).toFixed(2)}`,
    },
    {
      title: 'Quantità',
      key: 'quantita',
      render: (_, record) => {
        const isLowStock = record.quantita <= record.quantita_minima
        return (
          <Space>
            {isLowStock && <WarningOutlined style={{ color: 'red' }} />}
            <span style={{ color: isLowStock ? 'red' : 'inherit' }}>
              {record.quantita}
            </span>
            {record.quantita_minima > 0 && (
              <Tag color={isLowStock ? 'red' : 'default'}>
                Min: {record.quantita_minima}
              </Tag>
            )}
          </Space>
        )
      },
    },
    {
      title: 'Ubicazione',
      dataIndex: 'posizione_magazzino',
      key: 'posizione_magazzino',
      render: (posizione) => posizione || '-',
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
            title="Sei sicuro di voler eliminare questo ricambio?"
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
        title="Gestione Ricambi"
        extra={[
          <Input.Search
            key="search"
            placeholder="Cerca ricambio..."
            onSearch={setSearchText}
            style={{ width: 300 }}
            allowClear
          />,
          <Button
            key="add"
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            Nuovo Ricambio
          </Button>,
        ]}
      />

      <Table
        columns={columns}
        dataSource={data?.items}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize: 10,
          total: data?.total,
          onChange: setPage,
          showTotal: (total) => `Totale ${total} ricambi`,
        }}
      />

      <Modal
        title={editingPart ? 'Modifica Ricambio' : 'Nuovo Ricambio'}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false)
          form.resetFields()
        }}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="code"
              label="Codice Ricambio"
              rules={[{ required: true, message: 'Inserisci il codice' }]}
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="category"
              label="Categoria"
              style={{ flex: 1 }}
            >
              <Input placeholder="Es: Filtri, Freni, ecc." />
            </Form.Item>
          </Space>

          <Form.Item
            name="name"
            label="Nome Ricambio"
            rules={[{ required: true, message: 'Inserisci il nome' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="description"
            label="Descrizione"
          >
            <Input.TextArea rows={2} />
          </Form.Item>

          <Form.Item
            name="supplier"
            label="Fornitore"
          >
            <Input />
          </Form.Item>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="unit_price"
              label="Prezzo Unitario (€)"
              rules={[{ required: true, message: 'Inserisci il prezzo' }]}
              style={{ flex: 1 }}
            >
              <InputNumber
                min={0}
                step={0.01}
                precision={2}
                style={{ width: '100%' }}
                prefix="€"
              />
            </Form.Item>

            <Form.Item
              name="quantity"
              label="Quantità in Magazzino"
              rules={[{ required: true, message: 'Inserisci la quantità' }]}
              style={{ flex: 1 }}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="min_stock_level"
              label="Scorta Minima"
              style={{ flex: 1 }}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Space>

          <Form.Item
            name="location"
            label="Ubicazione Magazzino"
          >
            <Input placeholder="Es: Scaffale A3, Reparto 2, ecc." />
          </Form.Item>

          <Form.Item
            name="notes"
            label="Note"
          >
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default PartsPage
