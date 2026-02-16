import { useState } from 'react'
import { Table, Button, Modal, Form, Input, Select, Space, Tag, Popconfirm, message, InputNumber, Row, Col, Divider, Spin, AutoComplete } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, CarOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import PageHeader from '@/components/PageHeader'
import { useVehicles, useCreateVehicle, useUpdateVehicle, useDeleteVehicle } from '@/hooks/useVehicles'
import { useCustomers } from '@/hooks/useCustomers'
import { useMarche, useModelli, useCarburanti } from '@/hooks/useAuto'
import type { Vehicle } from '@/types'

const VehiclesPage = () => {
  const [page, setPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null)
  const [selectedMarca, setSelectedMarca] = useState<string>('')
  const [form] = Form.useForm()

  const { data, isLoading } = useVehicles(page, 10, searchText)
  const { data: customersData } = useCustomers(1, 1000) // Get all customers for select
  const createMutation = useCreateVehicle()
  const updateMutation = useUpdateVehicle()
  const deleteMutation = useDeleteVehicle()
  
  // Hooks per auto (marche, modelli, carburanti)
  const { data: marcheData, isLoading: loadingMarche } = useMarche()
  const { data: modelliData, isLoading: loadingModelli } = useModelli(selectedMarca)
  const { data: carburanti } = useCarburanti()

  const handleCreate = () => {
    setEditingVehicle(null)
    setSelectedMarca('')
    form.resetFields()
    setIsModalOpen(true)
  }

  const handleEdit = (record: Vehicle) => {
    setEditingVehicle(record)
    setSelectedMarca(record.marca || '')
    form.setFieldsValue(record)
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
