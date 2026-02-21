import { Modal, Form, Input, Select, message, Button, Row, Col } from 'antd'
import { useEffect, useState } from 'react'
import axiosInstance from '@/lib/axios'

interface UserFormModalProps {
  open: boolean
  editingUser: any | null
  onOk: (values: any) => void
  onCancel: () => void
  loading?: boolean
}

export const UserFormModal = ({ open, editingUser, onOk, onCancel, loading }: UserFormModalProps) => {
  const [form] = Form.useForm()
  const [renderKey, setRenderKey] = useState(0)
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [roleOptions, setRoleOptions] = useState<any[]>([])
  const [loadingRoles, setLoadingRoles] = useState(false)

  // Carica i ruoli dal backend quando il componente monta
  useEffect(() => {
    const fetchRoles = async () => {
      try {
        setLoadingRoles(true)
        const response = await axiosInstance.get('/permissions/roles')
        setRoleOptions(response.data.roles || [])
      } catch (error) {
        console.error('Errore caricamento ruoli:', error)
        message.error('Impossibile caricare i ruoli')
      } finally {
        setLoadingRoles(false)
      }
    }
    fetchRoles()
  }, [])

  // When modal opens, increment renderKey to force complete Form re-render
  useEffect(() => {
    if (open) {
      console.log('🔄 Modal opened - Incrementing renderKey to force Form re-render')
      setRenderKey(prev => prev + 1)
      setPassword('')
      setPasswordConfirm('')
    }
  }, [open])

  const validatePasswordFields = (): boolean => {
    if (!editingUser && !password) {
      message.error('Password obbligatoria')
      return false
    }
    
    if (password) {
      if (password.length < 5) {
        message.error('La password deve essere almeno 5 caratteri')
        return false
      }
      if (password.length > 12) {
        message.error('La password non può superare 12 caratteri')
        return false
      }
      if (!/[a-z]/.test(password)) {
        message.error('La password deve contenere almeno una lettera minuscola')
        return false
      }
      if (!/[A-Z]/.test(password)) {
        message.error('La password deve contenere almeno una lettera maiuscola')
        return false
      }
      if (!/\d/.test(password)) {
        message.error('La password deve contenere almeno un numero')
        return false
      }
    }
    
    if (password !== passwordConfirm) {
      message.error('Le password non corrispondono')
      return false
    }
    
    return true
  }

  const handleSubmit = async () => {
    try {
      // Valida i campi password PRIMA di validare il form
      if (!validatePasswordFields()) {
        return
      }
      
      const values = await form.validateFields()
      
      console.log('📤 Form values:', values)
      
      // Rimappo i campi per il backend - OBBLIGATORI
      const payload: any = {
        username: values.user_handle?.trim() || '',
        email: values.email?.trim() || '',
        nome: values.nome?.trim() || '',
        cognome: values.cognome?.trim() || '',
        ruolo: values.ruolo || '',
        attivo: values.attivo === true || values.attivo === undefined,
        password: password || undefined
      }
      
      // Validazione manuale dei campi obbligatori
      if (!payload.username) {
        message.error('Username obbligatorio')
        return
      }
      if (!payload.email) {
        message.error('Email obbligatoria')
        return
      }
      if (!payload.nome) {
        message.error('Nome obbligatorio')
        return
      }
      if (!payload.cognome) {
        message.error('Cognome obbligatorio')
        return
      }
      if (!payload.ruolo) {
        message.error('Ruolo obbligatorio')
        return
      }
      
      // Rimuovo password se vuota (edit mode)
      if (!payload.password) {
        delete payload.password
      }
      
      console.log('📤 Final payload to backend:', JSON.stringify(payload, null, 2))
      onOk(payload)
      
      // Reset password fields after success
      setPassword('')
      setPasswordConfirm('')
    } catch (error) {
      console.error('❌ Validation error:', error)
      if (error instanceof Error) {
        message.error(`Errore: ${error.message}`)
      }
    }
  }

  return (
    <Modal
      key={`modal-${open}-${editingUser?.id || 'create'}`}
      title={editingUser ? 'Modifica Utente' : 'Nuovo Utente'}
      open={open}
      onOk={handleSubmit}
      onCancel={onCancel}
      destroyOnHidden={true}
      width={600}
      style={{ maxHeight: '90vh' }}
      styles={{ body: { maxHeight: 'calc(90vh - 200px)', overflowY: 'auto', padding: '16px' } }}
      okText="Salva"
      cancelText="Annulla"
      confirmLoading={loading}
    >
      {/* Render Form ONLY when modal is open to ensure clean state */}
      {open && (
        <FormContent
          key={`form-${renderKey}-${editingUser?.id || 'create'}`}
          form={form}
          editingUser={editingUser}
          password={password}
          setPassword={setPassword}
          passwordConfirm={passwordConfirm}
          setPasswordConfirm={setPasswordConfirm}
          roleOptions={roleOptions}
          loadingRoles={loadingRoles}
        />
      )}
    </Modal>
  )
}

// Separate component for form to ensure complete re-render
const FormContent = ({ 
  form, 
  editingUser,
  password,
  setPassword,
  passwordConfirm,
  setPasswordConfirm,
  roleOptions,
  loadingRoles
}: any) => {
  const [showPwdFieldsLocal, setShowPwdFieldsLocal] = useState(false)

  useEffect(() => {
    console.log('📝 FormContent useEffect - editingUser:', editingUser?.email)
    
    // Small delay to ensure Form is fully mounted
    setTimeout(() => {
      if (editingUser) {
        console.log('📝 EDIT - Setting values for:', editingUser.email)
      // In EDIT mode: popola CON i dati dell'utente
        form.setFieldsValue({
          email: editingUser.email || '',
          user_handle: editingUser.username || '',
          nome: editingUser.nome || '',
          cognome: editingUser.cognome || '',
          ruolo: editingUser.ruolo || undefined,
          attivo: editingUser.attivo === true || editingUser.attivo === 1
        })
        // Per la password in edit mode, nascondi i campi e resetta
        setShowPwdFieldsLocal(false)
        setPassword('')
        setPasswordConfirm('')
      } else {
        console.log('🆕 CREATE - Setting form to empty values')
        form.resetFields()
        setTimeout(() => {
          form.setFieldsValue({
            email: '',
            user_handle: '',
            nome: '',
            cognome: '',
            ruolo: undefined,
            attivo: true
          })
          console.log('🆕 All form fields set to empty')
          setPassword('')
          setPasswordConfirm('')
        }, 50)
      }
    }, 50)
  }, [editingUser, form, setPassword, setPasswordConfirm])

  return (
    <Form
      form={form}
      layout="vertical"
      style={{ marginTop: 0 }}
    >
      <Row gutter={12}>
        <Col span={16}>
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Email obbligatoria' },
              { type: 'email', message: 'Email non valida' }
            ]}
            style={{ marginBottom: '12px' }}
          >
            <Input type="email" placeholder="utente@garage.local" autoComplete="off" size="small" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item
            name="user_handle"
            label="Username"
            rules={[
              { required: true, message: 'Username obbligatorio' },
              { min: 3, message: 'Min 3 car' }
            ]}
            style={{ marginBottom: '12px' }}
          >
            <Input 
              placeholder="username" 
              autoComplete="off"
              size="small"
              spellCheck="false"
              data-lpignore="true"
              data-form-type="other"
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={12}>
        <Col span={12}>
          <Form.Item
            name="nome"
            label="Nome"
            rules={[{ required: true, message: 'Nome obbligatorio' }]}
            style={{ marginBottom: '12px' }}
          >
            <Input placeholder="Nome" size="small" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="cognome"
            label="Cognome"
            rules={[{ required: true, message: 'Cognome obbligatorio' }]}
            style={{ marginBottom: '12px' }}
          >
            <Input placeholder="Cognome" size="small" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={12}>
        <Col span={12}>
          <Form.Item
            name="ruolo"
            label="Ruolo"
            rules={[{ required: true, message: 'Seleziona un ruolo' }]}
            style={{ marginBottom: '12px' }}
          >
            <Select
              placeholder="Ruolo"
              options={roleOptions}
              size="small"
            />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="attivo"
            label="Stato"
            style={{ marginBottom: '12px' }}
          >
            <Select
              placeholder="Stato"
              options={[
                { label: '✅ Attivo', value: true },
                { label: '❌ Inattivo', value: false }
              ]}
              size="small"
            />
          </Form.Item>
        </Col>
      </Row>

      {/* PASSWORD SECTION - DIFFERENTE TRA CREATE E EDIT MODE */}
      {!editingUser || showPwdFieldsLocal ? (
        <>
          <Row gutter={12}>
            <Col span={12}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, fontSize: '12px' }}>
                  Password {!editingUser && <span style={{ color: 'red' }}>*</span>}
                </label>
                <input
                  type="text"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Abc12 (5-12 car)"
                  autoComplete="off"
                  data-lpignore="true"
                  data-form-type="other"
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '2px',
                    fontSize: '13px',
                    fontFamily: 'inherit',
                    WebkitTextSecurity: 'disc'
                  } as any}
                />
              </div>
            </Col>
            <Col span={12}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, fontSize: '12px' }}>
                  Conferma
                </label>
                <input
                  type="text"
                  value={passwordConfirm}
                  onChange={(e) => setPasswordConfirm(e.target.value)}
                  placeholder="Ripeti"
                  autoComplete="off"
                  data-lpignore="true"
                  data-form-type="other"
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '2px',
                    fontSize: '13px',
                    fontFamily: 'inherit',
                    WebkitTextSecurity: 'disc'
                  } as any}
                />
              </div>
            </Col>
          </Row>

          {editingUser && showPwdFieldsLocal && (
            <div style={{ marginBottom: '12px' }}>
              <Button 
                size="small"
                onClick={() => {
                  setShowPwdFieldsLocal(false)
                  setPassword('')
                  setPasswordConfirm('')
                }}
              >
                ❌ Annulla
              </Button>
            </div>
          )}
        </>
      ) : (
        <div style={{
          padding: '10px 12px',
          backgroundColor: '#f0f2f5',
          borderRadius: '4px',
          marginBottom: '12px',
          fontSize: '13px'
        }}>
          <div style={{ fontWeight: 500, marginBottom: '6px' }}>
            🔐 Password protetta
          </div>
          <Button 
            type="primary"
            size="small"
            onClick={() => setShowPwdFieldsLocal(true)}
          >
            ✏️ Modifica
          </Button>
        </div>
      )}
    </Form>
  )
}
