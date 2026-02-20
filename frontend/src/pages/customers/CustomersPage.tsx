import { useState } from 'react'
import { Table, Button, Space, Tag, Popconfirm, message, Input } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, PhoneOutlined, MailOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import PageHeader from '@/components/PageHeader'
import CustomerFormModal from '@/components/CustomerFormModal'
import { useCustomers, useDeleteCustomer } from '@/hooks/useCustomers'
import type { Customer } from '@/types'

const CustomersPage = () => {
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null)
  const deleteMutation = useDeleteCustomer()

  // Carica tutti i clienti per permettere ordinamento completo
  const { data, isLoading } = useCustomers(1, 1000, searchText)

  const handleCreate = () => {
    setEditingCustomer(null)
    setIsModalOpen(true)
  }

  const handleEdit = (record: Customer) => {
    setEditingCustomer(record)
    setIsModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    await deleteMutation.mutateAsync(id)
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
      sorter: (a, b) => {
        const nameA = a.tipo === 'azienda' ? (a.ragione_sociale || '') : `${a.nome || ''} ${a.cognome || ''}`.trim().toLowerCase()
        const nameB = b.tipo === 'azienda' ? (b.ragione_sociale || '') : `${b.nome || ''} ${b.cognome || ''}`.trim().toLowerCase()
        return nameA.localeCompare(nameB, 'it')
      },
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
          pageSize: 10,
          showTotal: (total) => `Totale ${total} clienti`,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
        }}
      />

      <CustomerFormModal
        open={isModalOpen}
        editingCustomer={editingCustomer}
        onCancel={() => setIsModalOpen(false)}
        onSuccess={() => {
          setIsModalOpen(false)
          setEditingCustomer(null)
        }}
      />
    </div>
  )
}

export default CustomersPage
