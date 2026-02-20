import { useState } from 'react'
import { Table, Button, Input, Space, Tag, Popconfirm, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, CarOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import PageHeader from '@/components/PageHeader'
import VehicleFormModal from '@/components/VehicleFormModal'
import { useVehicles, useDeleteVehicle } from '@/hooks/useVehicles'
import { useCustomers } from '@/hooks/useCustomers'
import type { Vehicle } from '@/types'

const VehiclesPage = () => {
  const [page, setPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null)
  const [sortField, setSortField] = useState<string | undefined>('targa')
  const [sortOrder, setSortOrder] = useState<'ascend' | 'descend' | undefined>('ascend')

  // Recupera TUTTI i veicoli per il sorting
  const { data: allVehiclesData, isLoading } = useVehicles(1, 10000, searchText)
  const { data: customersData } = useCustomers(1, 1000)
  const deleteMutation = useDeleteVehicle()

  // Funzione per ordinare e paginare i dati
  const getSortedAndPaginatedData = () => {
    if (!allVehiclesData?.items) return { items: [], total: 0 }

    let sortedData = [...allVehiclesData.items]

    // Applica sorting solo se sortField e sortOrder sono definiti
    if (sortField && sortOrder) {
      sortedData.sort((a, b) => {
        let aValue: any = a[sortField as keyof Vehicle]
        let bValue: any = b[sortField as keyof Vehicle]

        // Se ordunare  i valori null
        if (aValue == null && bValue == null) return 0
        if (aValue == null) return sortOrder === 'ascend' ? 1 : -1
        if (bValue == null) return sortOrder === 'ascend' ? -1 : 1

        // Comparazione per stringhe
        if (typeof aValue === 'string') {
          aValue = aValue.toLowerCase()
          bValue = (bValue as string).toLowerCase()
          return sortOrder === 'ascend'
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue)
        }

        // Comparazione per numeri e boolean
        if (typeof aValue === 'number' || typeof aValue === 'boolean') {
          return sortOrder === 'ascend' ? (aValue > bValue ? 1 : -1) : (aValue < bValue ? 1 : -1)
        }

        return 0
      })
    }

    // Applica paginazione
    const pageSize = 10
    const startIdx = (page - 1) * pageSize
    const endIdx = startIdx + pageSize
    const paginatedItems = sortedData.slice(startIdx, endIdx)

    return {
      items: paginatedItems,
      total: sortedData.length,
    }
  }

  const displayData = getSortedAndPaginatedData()

  const handleCreate = () => {
    setEditingVehicle(null)
    setIsModalOpen(true)
  }

  const handleEdit = (record: Vehicle) => {
    setEditingVehicle(record)
    setIsModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    await deleteMutation.mutateAsync(id)
  }

  // Helper function per trovare il cliente per ID
  const getCustomerName = (customerId: number) => {
    if (!customersData?.items) return '-'
    const customer = customersData.items.find(c => c.id === customerId)
    if (!customer) return '-'
    if (customer.tipo?.toLowerCase() === 'azienda') {
      return customer.ragione_sociale || '-'
    }
    return `${customer.nome || ''} ${customer.cognome || ''}`.trim() || '-'
  }

  const columns: ColumnsType<Vehicle> = [
    {
      title: 'Targa',
      dataIndex: 'targa',
      key: 'targa',
      sorter: true,
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
      sorter: true,
      render: (_, record) => `${record.marca} ${record.modello}`,
    },
    {
      title: 'Anno',
      dataIndex: 'anno',
      key: 'anno',
      sorter: true,
      render: (year) => year || '-',
    },
    {
      title: 'Colore',
      dataIndex: 'colore',
      key: 'colore',
      sorter: true,
      render: (colore) => colore || '-',
    },
    {
      title: 'Cliente',
      key: 'customer',
      sorter: true,
      render: (_, record) => getCustomerName(record.customer_id),
    },
    {
      title: 'KM Attuali',
      dataIndex: 'km_attuali',
      key: 'km_attuali',
      sorter: true,
      render: (km) => km ? `${km.toLocaleString()} km` : '-',
    },
    {
      title: 'Auto di Cortesia',
      dataIndex: 'courtesy_car',
      key: 'courtesy_car',
      sorter: true,
      render: (isCourtesyCar) => (
        <Tag color={isCourtesyCar ? 'green' : 'default'}>
          {isCourtesyCar ? '✅ Sì' : '❌ No'}
        </Tag>
      ),
      width: 140,
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
        dataSource={displayData.items}
        rowKey="id"
        loading={isLoading}
        onChange={(pagination, filters, sorter: any) => {
          // Gestione del sorting - gestisce il ciclo ascend -> descend -> undefined
          if (sorter && sorter.order) {
            // Se c'è un order definito (ascend o descend)
            setSortField(sorter.field || sorter.column?.dataIndex || 'targa')
            setSortOrder(sorter.order)
          } else {
            // Se sorter è undefined o order è undefined, resetta il sorting
            setSortField(undefined)
            setSortOrder(undefined)
          }
          // Reset a pagina 1 quando cambia l'ordinamento
          setPage(1)
        }}
        pagination={{
          current: page,
          pageSize: 10,
          total: displayData.total,
          onChange: setPage,
          showTotal: (total) => `Totale ${total} veicoli`,
        }}
      />

      <VehicleFormModal
        open={isModalOpen}
        editingVehicle={editingVehicle}
        onCancel={() => {
          setIsModalOpen(false)
          setEditingVehicle(null)
        }}
        onSuccess={() => {
          setIsModalOpen(false)
          setEditingVehicle(null)
        }}
      />
    </div>
  )
}

export default VehiclesPage
