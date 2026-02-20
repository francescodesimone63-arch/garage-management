import { Modal, Form, Input, Select, Row, Col, message, Tabs } from 'antd'
import { useState } from 'react'
import { useCreateCustomer, useUpdateCustomer } from '@/hooks/useCustomers'
import { useCustomerTypes } from '@/hooks/useSystemTables'
import type { Customer } from '@/types'

interface CustomerFormModalProps {
  open: boolean
  onSuccess: (customer: Customer) => void
  onCancel: () => void
  editingCustomer?: Customer | null
}

const CustomerFormModal = ({ open, onSuccess, onCancel, editingCustomer }: CustomerFormModalProps) => {
  const [form] = Form.useForm()
  const [customerType, setCustomerType] = useState<string>('Privato')
  const [activeTab, setActiveTab] = useState('info')
  const createMutation = useCreateCustomer()
  const updateMutation = useUpdateCustomer()
  const { data: customerTypes } = useCustomerTypes()

  const handleSubmit = async (values: any) => {
    try {
      // Normalizza tipo a lowercase per il backend
      const normalized = {
        ...values,
        tipo: values.tipo ? values.tipo.toLowerCase() : undefined,
      }
      
      let response: Customer
      if (editingCustomer) {
        response = await updateMutation.mutateAsync({ id: editingCustomer.id, data: normalized })
        message.success('Cliente aggiornato con successo')
      } else {
        response = await createMutation.mutateAsync(normalized)
        message.success('Cliente creato con successo')
      }
      
      form.resetFields()
      setCustomerType('Privato')
      setActiveTab('info')
      onSuccess(response)
      onCancel()
    } catch (error) {
      message.error(editingCustomer ? 'Errore durante l\'aggiornamento' : 'Errore durante il salvataggio')
    }
  }

  const handleCancel = () => {
    form.resetFields()
    setCustomerType('Privato')
    setActiveTab('info')
    onCancel()
  }

  return (
    <Modal
      title={editingCustomer ? 'Modifica Cliente' : 'Nuovo Cliente'}
      open={open}
      onCancel={handleCancel}
      onOk={() => form.submit()}
      confirmLoading={editingCustomer ? updateMutation.isPending : createMutation.isPending}
      width={700}
      okText="Salva"
      cancelText="Annulla"
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{ tipo: 'Privato', ...editingCustomer }}
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
                    name="tipo"
                    label="Tipo Cliente"
                    rules={[{ required: true, message: 'Seleziona il tipo' }]}
                    required
                  >
                    <Select placeholder="Seleziona un tipo" onChange={(value) => setCustomerType(value)}>
                      {customerTypes?.filter(ct => ct.attivo).map(ct => (
                        <Select.Option key={ct.id} value={ct.nome}>
                          {ct.nome}
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>

                  {customerType === 'Azienda' ? (
                    <Form.Item
                      name="ragione_sociale"
                      label="Ragione Sociale"
                      rules={[{ required: true, message: 'Inserisci la ragione sociale' }]}
                      required
                    >
                      <Input placeholder="es. Carrozzeria Rossi S.r.l." />
                    </Form.Item>
                  ) : (
                    <>
                      <Row gutter={12}>
                        <Col span={12}>
                          <Form.Item
                            name="nome"
                            label="Nome"
                            rules={[{ required: true, message: 'Inserisci il nome' }]}
                            required
                          >
                            <Input size="small" />
                          </Form.Item>
                        </Col>
                        <Col span={12}>
                          <Form.Item
                            name="cognome"
                            label="Cognome"
                            rules={[{ required: true, message: 'Inserisci il cognome' }]}
                            required
                          >
                            <Input size="small" />
                          </Form.Item>
                        </Col>
                      </Row>
                    </>
                  )}
                </>
              ),
            },
            {
              key: 'contact',
              label: 'Contatti',
              children: (
                <>
                  <Form.Item
                    name="email"
                    label="Email"
                    rules={[{ type: 'email', message: 'Email non valida' }]}
                  >
                    <Input size="small" placeholder="email@esempio.com" />
                  </Form.Item>

                  <Row gutter={12}>
                    <Col span={12}>
                      <Form.Item name="telefono" label="Telefono">
                        <Input size="small" placeholder="Fisso" />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="cellulare" label="Cellulare">
                        <Input size="small" placeholder="Mobile" />
                      </Form.Item>
                    </Col>
                  </Row>
                </>
              ),
            },
            {
              key: 'docs',
              label: 'Documenti',
              children: (
                <>
                  <Row gutter={12}>
                    <Col span={12}>
                      <Form.Item
                        name="codice_fiscale"
                        label="Codice Fiscale"
                        tooltip="Opzionale"
                      >
                        <Input size="small" placeholder="RSSMRA80A01H501U" />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="partita_iva"
                        label="Partita IVA"
                        tooltip="Per aziende"
                      >
                        <Input size="small" placeholder="11 cifre" maxLength={11} />
                      </Form.Item>
                    </Col>
                  </Row>
                </>
              ),
            },
            {
              key: 'address',
              label: 'Indirizzo',
              children: (
                <>
                  <Form.Item name="indirizzo" label="Indirizzo">
                    <Input size="small" />
                  </Form.Item>

                  <Row gutter={8}>
                    <Col span={12}>
                      <Form.Item name="citta" label="Città">
                        <Input size="small" />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="provincia" label="Prov">
                        <Input size="small" maxLength={2} />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="cap" label="CAP">
                        <Input size="small" />
                      </Form.Item>
                    </Col>
                  </Row>
                </>
              ),
            },
            {
              key: 'notes',
              label: 'Note',
              children: (
                <Form.Item name="note" label="">
                  <Input.TextArea rows={4} placeholder="Aggiungi note..." />
                </Form.Item>
              ),
            },
          ]}
        />
      </Form>
    </Modal>
  )
}

export default CustomerFormModal

