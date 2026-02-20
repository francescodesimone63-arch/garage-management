import { Modal, Form, Input, Select, Row, Col, InputNumber, Checkbox, Spin, AutoComplete, message, Tabs } from 'antd'
import { useCreateVehicle, useUpdateVehicle } from '@/hooks/useVehicles'
import { useCustomers } from '@/hooks/useCustomers'
import { useMarche, useModelli, useCarburanti } from '@/hooks/useAuto'
import type { Vehicle } from '@/types'
import { useState, useEffect } from 'react'

interface VehicleFormModalProps {
  open: boolean
  onSuccess: (vehicle: Vehicle) => void
  onCancel: () => void
  editingVehicle?: Vehicle | null
  preSelectedCustomerId?: number // Cliente pre-selezionato (non modificabile)
}

const VehicleFormModal = ({ open, onSuccess, onCancel, editingVehicle, preSelectedCustomerId }: VehicleFormModalProps) => {
  const [form] = Form.useForm()
  const [selectedMarca, setSelectedMarca] = useState<string>('')
  const [isTiberCar, setIsTiberCar] = useState(false)
  const [activeTab, setActiveTab] = useState('info')

  const createMutation = useCreateVehicle()
  const updateMutation = useUpdateVehicle()
  const { data: customersData } = useCustomers(1, 1000)
  const { data: marcheData, isLoading: loadingMarche } = useMarche()
  const { data: modelliData, isLoading: loadingModelli } = useModelli(selectedMarca)
  const { data: carburanti } = useCarburanti()

  // Per-compilare il cliente quando la modale si apre con preSelectedCustomerId
  useEffect(() => {
    if (open && preSelectedCustomerId && !editingVehicle) {
      form.setFieldValue('customer_id', preSelectedCustomerId)
      const customer = customersData?.items.find(c => c.id === preSelectedCustomerId)
      if (customer) {
        setIsTiberCar(customer.ragione_sociale === 'Tiber Car')
      }
    }
  }, [open, preSelectedCustomerId, editingVehicle, form, customersData])

  const handleMarcaChange = (value: string) => {
    setSelectedMarca(value)
    form.setFieldValue('modello', undefined)
    form.setFieldValue('marca', value)
  }

  const handleSubmit = async (values: any) => {
    try {
      // Ripulisci i valori: converti empty strings in null per campi opzionali
      const cleanedValues = Object.fromEntries(
        Object.entries(values)
          .filter(([_, v]) => v !== undefined)
          .map(([k, v]) => {
            // Converti stringhe vuote in null per marca, modello (opzionali)
            if ((k === 'marca' || k === 'modello') && v === '') {
              return [k, null]
            }
            return [k, v]
          })
      )
      
      let response: Vehicle
      if (editingVehicle) {
        response = await updateMutation.mutateAsync({
          id: editingVehicle.id,
          data: cleanedValues
        })
        message.success('Veicolo aggiornato con successo')
      } else {
        response = await createMutation.mutateAsync(cleanedValues)
        message.success('Veicolo creato con successo')
      }
      form.resetFields()
      setSelectedMarca('')
      setIsTiberCar(false)
      setActiveTab('info')
      onSuccess(response)
      onCancel()
    } catch (error: any) {
      console.error('🔴 Errore veicolo:', error)
      const errorMessage = error?.response?.data?.detail || error?.message || (editingVehicle ? 'Errore durante l\'aggiornamento' : 'Errore durante la creazione del veicolo')
      message.error(errorMessage)
    }
  }

  const handleCancel = () => {
    form.resetFields()
    setSelectedMarca('')
    setIsTiberCar(false)
    setActiveTab('info')
    onCancel()
  }

  return (
    <Modal
      title={editingVehicle ? 'Modifica Veicolo' : 'Nuovo Veicolo'}
      open={open}
      onCancel={handleCancel}
      onOk={() => form.submit()}
      confirmLoading={editingVehicle ? updateMutation.isPending : createMutation.isPending}
      width={750}
      okText="Salva"
      cancelText="Annulla"
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{ ...editingVehicle }}
        onValuesChange={(changed) => {
          if ('customer_id' in changed) {
            const customer = customersData?.items.find(c => c.id === changed.customer_id)
            setIsTiberCar(!!customer && customer.ragione_sociale === 'Tiber Car')
            if (!customer || customer.ragione_sociale !== 'Tiber Car') {
              form.setFieldValue('courtesy_car', false)
            }
          }
        }}
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'info',
              label: 'Informazioni',
              children: (
                <>
                  <Form.Item
                    name="customer_id"
                    label="Cliente"
                    rules={[{ required: true, message: 'Seleziona il cliente' }]}
                    required
                  >
                    <Select
                      showSearch
                      disabled={preSelectedCustomerId && !editingVehicle}
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

                  <Row gutter={12}>
                    <Col span={12}>
                      <Form.Item
                        name="targa"
                        label="Targa"
                        rules={[{ required: true, message: 'Inserisci la targa' }]}
                        required
                      >
                        <Input
                          size="small"
                          placeholder="XX000XX"
                          onChange={(e) => form.setFieldValue('targa', e.target.value.toUpperCase())}
                        />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="telaio" label="VIN">
                        <Input size="small" maxLength={17} placeholder="17 caratteri" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={12}>
                    <Col span={12}>
                      <Form.Item
                        name="marca"
                        label="Marca"
                        rules={[{ required: true, message: 'Inserisci la marca' }]}
                        required
                      >
                        <AutoComplete
                          size="small"
                          placeholder="Seleziona marca"
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
                        rules={[{ required: true, message: 'Inserisci il modello' }]}
                        required
                      >
                        <AutoComplete
                          size="small"
                          placeholder={selectedMarca ? 'Seleziona' : 'Marca prima'}
                          disabled={!selectedMarca}
                          filterOption={(input, option) =>
                            (option?.value ?? '').toLowerCase().includes(input.toLowerCase())
                          }
                          notFoundContent={loadingModelli ? <Spin size="small" /> : null}
                          options={modelliData?.modelli.map((modello) => ({
                            value: modello,
                            label: modello,
                          }))}
                        />
                      </Form.Item>
                    </Col>
                  </Row>
                </>
              ),
            },
            {
              key: 'technical',
              label: 'Dati Tecnici',
              children: (
                <>
                  <Row gutter={8}>
                    <Col span={6}>
                      <Form.Item
                        name="anno"
                        label="Anno"
                      >
                        <InputNumber size="small" min={1900} max={new Date().getFullYear() + 1} style={{ width: '100%' }} placeholder="Opzionale" />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="carburante" label="Carburante">
                        <Select
                          size="small"
                          placeholder="Tipo"
                          allowClear
                          options={carburanti?.map((c) => ({ value: c, label: c }))}
                        />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="colore" label="Colore">
                        <Input size="small" placeholder="es. Nero" />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="cilindrata" label="cc">
                        <Input size="small" placeholder="1598" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={8}>
                    <Col span={6}>
                      <Form.Item name="kw" label="KW">
                        <InputNumber size="small" min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="cv" label="CV">
                        <InputNumber size="small" min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="porte" label="Porte">
                        <Select
                          size="small"
                          placeholder="N."
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
                      <Form.Item name="prima_immatricolazione" label="Immatr.">
                        <Input size="small" type="date" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item name="km_attuali" label="Chilometri Attuali">
                    <InputNumber size="small" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </>
              ),
            },
            {
              key: 'cortesia',
              label: 'Cortesia',
              children: (
                <>
                  <Form.Item name="courtesy_car" valuePropName="checked">
                    <Checkbox disabled={!isTiberCar}>Auto di cortesia (Tiber Car)</Checkbox>
                  </Form.Item>

                  <Form.Item name="note" label="Note">
                    <Input.TextArea size="small" rows={3} />
                  </Form.Item>
                </>
              ),
            },
          ]}
        />
      </Form>
    </Modal>
  )
}

export default VehicleFormModal
