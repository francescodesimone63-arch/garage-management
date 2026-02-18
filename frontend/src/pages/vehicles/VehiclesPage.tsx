import { useState } from 'react'
import { Checkbox } from 'antd'
import { Table, Button, Modal, Form, Input, Select, Space, Tag, Popconfirm, message, InputNumber, Row, Col, Divider, Spin, AutoComplete } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, CarOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import PageHeader from '@/components/PageHeader'
import { useVehicles, useCreateVehicle, useUpdateVehicle, useDeleteVehicle } from '@/hooks/useVehicles'
import { useCustomers } from '@/hooks/useCustomers'
import { useMarche, useModelli, useCarburanti } from '@/hooks/useAuto'
import type { Vehicle } from '@/types'

const VehiclesPage = () => {
    // Stato per abilitazione checkbox courtesy_car
    const [isTiberCar, setIsTiberCar] = useState(false)
  const [page, setPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null)
  const [selectedMarca, setSelectedMarca] = useState<string>('')
  const [sortField, setSortField] = useState<string | undefined>('targa')
  const [sortOrder, setSortOrder] = useState<'ascend' | 'descend' | undefined>('ascend')
  const [form] = Form.useForm()

  // Recupera TUTTI i veicoli per il sorting
  const { data: allVehiclesData, isLoading } = useVehicles(1, 10000, searchText)
  const { data: customersData } = useCustomers(1, 1000) // Get all customers for select
  const createMutation = useCreateVehicle()
  const updateMutation = useUpdateVehicle()
  const deleteMutation = useDeleteVehicle()
  
  // Hooks per auto (marche, modelli, carburanti)
  const { data: marcheData, isLoading: loadingMarche } = useMarche()
  const { data: modelliData, isLoading: loadingModelli } = useModelli(selectedMarca)
  const { data: carburanti } = useCarburanti()

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
    setSelectedMarca('')
    form.resetFields()
    setIsTiberCar(false)
    setIsModalOpen(true)
  }

  const handleEdit = (record: Vehicle) => {
    setEditingVehicle(record)
    setSelectedMarca(record.marca || '')
    form.setFieldsValue(record)
    // Controlla se il cliente è Tiber Car
    const customer = customersData?.items.find(c => c.id === record.customer_id)
    setIsTiberCar(!!customer && (customer.ragione_sociale === 'Tiber Car'))
    setIsModalOpen(true)
  }

  // Gestione cambio marca (reset modello)
  const handleMarcaChange = (value: string) => {
    setSelectedMarca(value)
    form.setFieldValue('modello', undefined)
    form.setFieldValue('marca', value)
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

      <Modal
        title={editingVehicle ? 'Modifica Veicolo' : 'Nuovo Veicolo'}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false)
          form.resetFields()
          setSelectedMarca('')
        }}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        width={900}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          onValuesChange={(changed, all) => {
            if ('customer_id' in changed) {
              const customer = customersData?.items.find(c => c.id === changed.customer_id)
              setIsTiberCar(!!customer && (customer.ragione_sociale === 'Tiber Car'))
              if (!customer || customer.ragione_sociale !== 'Tiber Car') {
                form.setFieldValue('courtesy_car', false)
              }
            }
          }}
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
                label: c.tipo?.toLowerCase() === 'azienda'
                  ? (c.ragione_sociale || '(azienda senza nome)')
                  : `${c.nome || ''} ${c.cognome || ''}`.trim() || '(privato senza nome)',
              }))}
            />
          </Form.Item>

          <Divider orientation="left">
            <CarOutlined /> Targa e Identificazione
          </Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="targa"
                label="Targa"
                rules={[{ required: true, message: 'Inserisci la targa' }]}
              >
                <Input 
                  placeholder="XX000XX" 
                  onChange={(e) => form.setFieldValue('targa', e.target.value.toUpperCase())}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="telaio"
                label="Numero Telaio (VIN)"
              >
                <Input maxLength={17} placeholder="17 caratteri" />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">
            <CarOutlined /> Marca e Modello
          </Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="marca"
                label="Marca"
                rules={[{ required: true, message: 'Inserisci o seleziona la marca' }]}
              >
                <AutoComplete
                  placeholder="Seleziona o digita la marca"
                  value={selectedMarca || form.getFieldValue('marca')}
                  onChange={handleMarcaChange}
                  filterOption={(input, option) =>
                    (option?.value ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  notFoundContent={loadingMarche ? <Spin size="small" /> : null}
                  options={marcheData?.marche.map((marca) => ({
                    value: marca,
                    label: marca,
                  }))}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="modello"
                label="Modello"
                rules={[{ required: true, message: 'Inserisci o seleziona il modello' }]}
              >
                <AutoComplete
                  placeholder={selectedMarca ? 'Seleziona o digita il modello' : 'Prima seleziona la marca'}
                  disabled={!selectedMarca}
                  filterOption={(input, option) =>
                    (option?.value ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  notFoundContent={
                    loadingModelli ? (
                      <Spin size="small" />
                    ) : null
                  }
                  options={modelliData?.modelli.map((modello) => ({
                    value: modello,
                    label: modello,
                  }))}
                />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">Dati Tecnici</Divider>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item
                name="anno"
                label="Anno"
                rules={[{ required: true, message: 'Inserisci l\'anno' }]}
              >
                <InputNumber min={1900} max={new Date().getFullYear() + 1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="carburante"
                label="Carburante"
              >
                <Select
                  placeholder="Tipo"
                  allowClear
                  options={carburanti?.map((c) => ({ value: c, label: c }))}
                />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="cilindrata"
                label="Cilindrata"
              >
                <Input placeholder="es. 1598 cc" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="colore"
                label="Colore"
              >
                <Input placeholder="es. Nero, Bianco" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item
                name="kw"
                label="KW"
              >
                <InputNumber min={0} style={{ width: '100%' }} placeholder="es. 90" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="cv"
                label="CV"
              >
                <InputNumber min={0} style={{ width: '100%' }} placeholder="es. 122" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="porte"
                label="N° Porte"
              >
                <Select
                  placeholder="Porte"
                  allowClear
                  options={[
                    { value: 2, label: '2' },
                    { value: 3, label: '3' },
                    { value: 4, label: '4' },
                    { value: 5, label: '5' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="prima_immatricolazione"
                label="Prima Immatric."
              >
                <Input type="date" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="km_attuali"
                label="Chilometri Attuali"
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="courtesy_car"
            valuePropName="checked"
            label="Auto di cortesia"
          >
            <Checkbox disabled={!isTiberCar}>Auto di cortesia</Checkbox>
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
