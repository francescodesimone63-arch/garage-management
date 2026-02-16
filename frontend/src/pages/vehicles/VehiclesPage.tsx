import { useState } from 'react'
import { Table, Button, Modal, Form, Input, Select, Space, Tag, Popconfirm, message, InputNumber } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, CarOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import PageHeader from '@/components/PageHeader'
import { useVehicles, useCreateVehicle, useUpdateVehicle, useDeleteVehicle } from '@/hooks/useVehicles'
import { useCustomers } from '@/hooks/useCustomers'
import type { Vehicle } from '@/types'

const VehiclesPage = () => {
  const [page, setPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null)
  const [form] = Form.useForm()

  const { data, isLoading } = useVehicles(page, 10, searchText)
  const { data: customersData } = useCustomers(1, 1000) // Get all customers for select
  const createMutation = useCreateVehicle()
  const updateMutation = useUpdateVehicle()
  const deleteMutation = useDeleteVehicle()

  const handleCreate = () => {
    setEditingVehicle(null)
    form.resetFields()
    setIsModalOpen(true)
  }

  const handleEdit = (record: Vehicle) => {
    setEditingVehicle(record)
    form.setFieldsValue(record)
    setIsModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    await deleteMutation.mutateAsync(id)
  }

  const handleSubmit = async (values: any) => {
    try {
      if (editingVehicle) {
        await updateMutation.mutateAsync({ id: editingVehicle.id, data: values })
      } else {
        await createMutation.mutateAsync(values)
      }
      setIsModalOpen(false)
      form.resetFields()
    } catch (error) {
      message.error('Errore durante il salvataggio')
    }
  }

  const columns: ColumnsType<Vehicle> = [
    {
      title: 'Targa',
      dataIndex: 'targa',
      key: 'targa',
      render: (text) => (
        <Space>
          <CarOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: 'Veicolo',
      key: 'vehicle',
      render: (_, record) => `${record.marca} ${record.modello}`,
    },
    {
      title: 'Anno',
      dataIndex: 'anno',
      key: 'anno',
      render: (year) => year || '-',
    },
    {
      title: 'Colore',
      dataIndex: 'colore',
      key: 'colore',
      render: (colore) => colore || '-',
    },
    {
      title: 'Cliente',
      key: 'customer',
      render: (_, record) => 
        record.customer ? `${record.customer.nome} ${record.customer.cognome}` : '-',
    },
    {
      title: 'KM Attuali',
      dataIndex: 'km_attuali',
      key: 'km_attuali',
      render: (km) => km ? `${km.toLocaleString()} km` : '-',
    },
    {
      title: 'Stato',
      dataIndex: 'attivo',
      key: 'attivo',
      render: (attivo) => (
        <Tag color={attivo ? 'green' : 'red'}>
          {attivo ? 'Attivo' : 'Inattivo'}
        </Tag>
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
            title="Sei sicuro di voler eliminare questo veicolo?"
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
        title="Gestione Veicoli"
        extra={[
          <Input.Search
            key="search"
            placeholder="Cerca veicolo..."
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
            Nuovo Veicolo
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
          showTotal: (total) => `Totale ${total} veicoli`,
        }}
      />

      <Modal
        title={editingVehicle ? 'Modifica Veicolo' : 'Nuovo Veicolo'}
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
          <Form.Item
            name="customer_id"
            label="Cliente"
            rules={[{ required: true, message: 'Seleziona il cliente' }]}
          >
            <Select
              showSearch
              placeholder="Seleziona cliente"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={customersData?.items.map(c => ({
                value: c.id,
                label: `${c.nome} ${c.cognome}`,
              }))}
            />
          </Form.Item>

          <Form.Item
            name="targa"
            label="Targa"
            rules={[{ required: true, message: 'Inserisci la targa' }]}
          >
            <Input placeholder="XX000XX" />
          </Form.Item>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="marca"
              label="Marca"
              rules={[{ required: true, message: 'Inserisci la marca' }]}
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="modello"
              label="Modello"
              rules={[{ required: true, message: 'Inserisci il modello' }]}
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>
          </Space>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="anno"
              label="Anno"
              rules={[{ required: true, message: 'Inserisci l\'anno' }]}
              style={{ width: 120 }}
            >
              <InputNumber min={1900} max={new Date().getFullYear() + 1} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="colore"
              label="Colore"
              style={{ flex: 1 }}
            >
              <Input placeholder="es. Nero, Bianco, Grigio" />
            </Form.Item>
          </Space>

          <Form.Item
            name="telaio"
            label="Numero Telaio (VIN)"
          >
            <Input maxLength={17} placeholder="17 caratteri" />
          </Form.Item>

          <Form.Item
            name="km_attuali"
            label="Chilometri Attuali"
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="note"
            label="Note"
          >
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default VehiclesPage
