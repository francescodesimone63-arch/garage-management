import { useState } from 'react'
import { Table, Button, Modal, Form, Input, Space, Tag, Popconfirm, message, Select } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, PhoneOutlined, MailOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import PageHeader from '@/components/PageHeader'
import { useCustomers, useCreateCustomer, useUpdateCustomer, useDeleteCustomer } from '@/hooks/useCustomers'
import { useCustomerTypes } from '@/hooks/useSystemTables'
import type { Customer } from '@/types'

const CustomersPage = () => {
  const [page, setPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null)
  const [customerType, setCustomerType] = useState<string>('privato')
  const [form] = Form.useForm()

  const { data, isLoading } = useCustomers(page, 10, searchText)
  const createMutation = useCreateCustomer()
  const updateMutation = useUpdateCustomer()
  const deleteMutation = useDeleteCustomer()
  const { data: customerTypes } = useCustomerTypes()

  const handleCreate = () => {
    setEditingCustomer(null)
    setCustomerType('privato')
    form.resetFields()
    setIsModalOpen(true)
  }

  const handleEdit = (record: Customer) => {
    setEditingCustomer(record)
    setCustomerType(record.tipo || 'privato')
    form.setFieldsValue(record)
    setIsModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    await deleteMutation.mutateAsync(id)
  }

  const handleSubmit = async (values: any) => {
    try {
      if (editingCustomer) {
        await updateMutation.mutateAsync({ id: editingCustomer.id, data: values })
      } else {
        await createMutation.mutateAsync(values)
      }
      setIsModalOpen(false)
      form.resetFields()
    } catch (error) {
      message.error('Errore durante il salvataggio')
    }
  }

  const columns: ColumnsType<Customer> = [
    {
      title: 'Cliente',
      key: 'name',
      render: (_, record) => {
        if (record.tipo === 'azienda' && record.ragione_sociale) {
          return (
            <Space direction="vertical" size={0}>
              <strong>{record.ragione_sociale}</strong>
              <Tag color="blue" style={{ fontSize: '10px' }}>Azienda</Tag>
            </Space>
          )
        }
        return (
          <Space direction="vertical" size={0}>
            <span>{`${record.nome || ''} ${record.cognome || ''}`.trim()}</span>
            <Tag color="green" style={{ fontSize: '10px' }}>Privato</Tag>
          </Space>
        )
      },
      sorter: true,
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      render: (email) => email ? <><MailOutlined /> {email}</> : '-',
    },
    {
      title: 'Telefono',
      key: 'phone',
      render: (_, record) => {
        const phone = record.cellulare || record.telefono
        return phone ? <><PhoneOutlined /> {phone}</> : '-'
      },
    },
    {
      title: 'Codice Fiscale',
      dataIndex: 'codice_fiscale',
      key: 'codice_fiscale',
      render: (code) => code || '-',
    },
    {
      title: 'P.IVA',
      dataIndex: 'partita_iva',
      key: 'partita_iva',
      render: (vat) => vat || '-',
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
            title="Sei sicuro di voler eliminare questo cliente?"
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
        title="Gestione Clienti"
        extra={[
          <Input.Search
            key="search"
            placeholder="Cerca cliente..."
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
            Nuovo Cliente
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
          showTotal: (total) => `Totale ${total} clienti`,
        }}
      />

      <Modal
        title={editingCustomer ? 'Modifica Cliente' : 'Nuovo Cliente'}
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
          initialValues={{ tipo: 'privato' }}
        >
          <Form.Item
            name="tipo"
            label="Tipo Cliente"
            rules={[{ required: true, message: 'Seleziona il tipo' }]}
          >
            <Select onChange={(value) => setCustomerType(value)}>
              {customerTypes?.filter(ct => ct.attivo).map(customerType => (
                <Select.Option key={customerType.id} value={customerType.nome.toLowerCase()}>
                  {customerType.nome}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          {customerType === 'azienda' ? (
            <Form.Item
              name="ragione_sociale"
              label="Ragione Sociale"
              rules={[{ required: true, message: 'Inserisci la ragione sociale' }]}
            >
              <Input placeholder="es. Carrozzeria Rossi S.r.l." />
            </Form.Item>
          ) : (
            <>
              <Form.Item
                name="nome"
                label="Nome"
                rules={[{ required: true, message: 'Inserisci il nome' }]}
              >
                <Input />
              </Form.Item>

              <Form.Item
                name="cognome"
                label="Cognome"
                rules={[{ required: true, message: 'Inserisci il cognome' }]}
              >
                <Input />
              </Form.Item>
            </>
          )}

          <Form.Item
            name="email"
            label="Email"
            rules={[{ type: 'email', message: 'Email non valida' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="telefono"
            label="Telefono Fisso"
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="cellulare"
            label="Cellulare"
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="codice_fiscale"
            label="Codice Fiscale"
            tooltip="Opzionale ma consigliato"
          >
            <Input placeholder="Es. RSSMRA80A01H501U" />
          </Form.Item>

          <Form.Item
            name="partita_iva"
            label="Partita IVA"
            tooltip="Obbligatoria per aziende"
          >
            <Input placeholder="11 cifre" maxLength={11} />
          </Form.Item>

          <Form.Item
            name="indirizzo"
            label="Indirizzo"
          >
            <Input />
          </Form.Item>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="citta"
              label="Città"
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="provincia"
              label="Provincia"
              style={{ width: 100 }}
            >
              <Input maxLength={2} />
            </Form.Item>

            <Form.Item
              name="cap"
              label="CAP"
              style={{ width: 120 }}
            >
              <Input />
            </Form.Item>
          </Space>

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

export default CustomersPage
