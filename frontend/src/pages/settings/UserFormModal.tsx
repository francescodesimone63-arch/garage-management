import { Modal, Form, Input, Select, message, Button } from 'antd'
import { useEffect, useState } from 'react'

interface UserFormModalProps {
  open: boolean
  editingUser: any | null
  onOk: (values: any) => void
  onCancel: () => void
  loading?: boolean
}

const roleOptions = [
  { label: 'Amministratore', value: 'ADMIN' },
  { label: 'GM - Direttore', value: 'GENERAL_MANAGER' },
  { label: 'CMM - Meccanica', value: 'WORKSHOP' },
  { label: 'CBM - Carrozzeria', value: 'BODYSHOP' }
]

export const UserFormModal = ({ open, editingUser, onOk, onCancel, loading }: UserFormModalProps) => {
  const [form] = Form.useForm()
  const [renderKey, setRenderKey] = useState(0)
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')

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
      width={700}
      style={{ maxHeight: '90vh' }}
      bodyStyle={{ maxHeight: '70vh', overflowY: 'auto' }}
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
  setPasswordConfirm
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
      style={{ marginTop: 20 }}
    >
      <Form.Item
        name="email"
        label="Email"
        rules={[
          { required: true, message: 'Email obbligatoria' },
          { type: 'email', message: 'Email non valida' }
        ]}
      >
        <Input type="email" placeholder="utente@garage.local" autoComplete="off" />
      </Form.Item>

      <Form.Item
        name="user_handle"
        label="Username"
        rules={[
          { required: true, message: 'Username obbligatorio' },
          { min: 3, message: 'Minimo 3 caratteri' }
        ]}
      >
        <Input 
          placeholder="username" 
          autoComplete="off"
          spellCheck="false"
          data-lpignore="true"
          data-form-type="other"
        />
      </Form.Item>

      <Form.Item
        name="nome"
        label="Nome"
        rules={[{ required: true, message: 'Nome obbligatorio' }]}
      >
        <Input placeholder="Nome" />
      </Form.Item>

      <Form.Item
        name="cognome"
        label="Cognome"
        rules={[{ required: true, message: 'Cognome obbligatorio' }]}
      >
        <Input placeholder="Cognome" />
      </Form.Item>

      <Form.Item
        name="ruolo"
        label="Ruolo"
        rules={[{ required: true, message: 'Seleziona un ruolo' }]}
      >
        <Select
          placeholder="Seleziona ruolo"
          options={roleOptions}
        />
      </Form.Item>

      <Form.Item
        name="attivo"
        label="Stato Utente"
      >
        <Select
          placeholder="Seleziona stato"
          options={[
            { label: 'Attivo ✅', value: true },
            { label: 'Inattivo ❌', value: false }
          ]}
        />
      </Form.Item>

      {/* PASSWORD SECTION - DIFFERENTE TRA CREATE E EDIT MODE */}
      {!editingUser || showPwdFieldsLocal ? (
        <>
          {/* PASSWORD - HTML PURO, SENZA TYPE PASSWORD CHE ATTIVA AUTOCOMPLETE */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
              Password {!editingUser && <span style={{ color: 'red' }}>*</span>}
            </label>
            <input
              type="text"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="5-12 char: maiusc+minusc+numero (es: Abc12)"
              autoComplete="off"
              data-lpignore="true"
              data-form-type="other"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #d9d9d9',
                borderRadius: '2px',
                fontSize: '14px',
                fontFamily: 'inherit',
                WebkitTextSecurity: 'disc' // Maschera come • (Chrome, Safari)
              } as any}
            />
            <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
              {editingUser && showPwdFieldsLocal ? 'Lascia vuoto per mantenere la password attuale' : 'Obbligatorio'}
            </div>
          </div>

          {/* CONFERMA PASSWORD - STESSO APPROCCIO */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
              Conferma Password
            </label>
            <input
              type="text"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              placeholder="Ripeti password"
              autoComplete="off"
              data-lpignore="true"
              data-form-type="other"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #d9d9d9',
                borderRadius: '2px',
                fontSize: '14px',
                fontFamily: 'inherit',
                WebkitTextSecurity: 'disc' // Maschera come • (Chrome, Safari)
              } as any}
            />
          </div>

          {editingUser && showPwdFieldsLocal && (
            <div style={{ marginBottom: '24px' }}>
              <Button 
                onClick={() => {
                  setShowPwdFieldsLocal(false)
                  setPassword('')
                  setPasswordConfirm('')
                }}
              >
                ❌ Annulla cambio password
              </Button>
            </div>
          )}
        </>
      ) : (
        // EDIT MODE - Password non modificata
        <div style={{
          padding: '12px',
          backgroundColor: '#f0f2f5',
          borderRadius: '4px',
          marginBottom: '24px'
        }}>
          <div style={{ fontSize: '14px', fontWeight: 500, marginBottom: '8px' }}>
            🔐 Password attuale
          </div>
          <div style={{ fontSize: '13px', color: '#666', marginBottom: '12px' }}>
            La password rimarrà invariata. Clicca il bottone qui sotto solo se vuoi cambiarla.
          </div>
          <Button 
            type="primary"
            onClick={() => setShowPwdFieldsLocal(true)}
          >
            ✏️ Cambia password
          </Button>
        </div>
      )}
    </Form>
  )
}
