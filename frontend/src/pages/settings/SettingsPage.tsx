import { useState, useEffect } from 'react'
import { Table, Button, Space, message, Card, Tabs, Popconfirm } from 'antd'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import PageHeader from '@/components/PageHeader'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import { UserFormModal } from './UserFormModal'
import { SystemTableManager } from '@/components/SystemTableManager'
import { InterventionStatusTypeManager } from '@/components/InterventionStatusTypeManager'

interface User {
  id: number
  email: string
  nome?: string
  cognome?: string
  username?: string
  ruolo: string
  attivo: boolean
  created_at: string
  updated_at: string
}

const SettingsPage = () => {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)

  // Load users on component mount
  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get<{ items?: User[]; _items?: User[] }>(
        API_ENDPOINTS.USERS
      )
      // Handle both possible response formats
      const userData = response.data.items || response.data._items || response.data || []
      setUsers(Array.isArray(userData) ? userData : [])
    } catch (error) {
      console.error('Errore nel caricamento utenti:', error)
      message.error('Errore nel caricamento utenti')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    console.log('🆕 handleCreate called')
    setEditingUser(null)
    setIsModalOpen(true)
    console.log('🆕 After setIsModalOpen(true) - isModalOpen should be true now')
  }

  const handleEdit = (user: User) => {
    console.log('📝 handleEdit called for:', user.email)
    setEditingUser(user)
    setIsModalOpen(true)
  }

  const handleDelete = async (userId: number) => {
    try {
      await axiosInstance.delete(`${API_ENDPOINTS.USERS}${userId}`)
      message.success('Utente eliminato con successo')
      loadUsers()
    } catch (error) {
      console.error('Errore:', error)
      message.error('Errore durante l\'eliminazione dell\'utente')
    }
  }

  const handleModalOkValues = async (values: any) => {
    try {
      if (editingUser) {
        // Update existing user
        await axiosInstance.put(`${API_ENDPOINTS.USERS}${editingUser.id}`, values)
        message.success('Utente aggiornato con successo')
      } else {
        // Create new user
        await axiosInstance.post(API_ENDPOINTS.USERS, values)
        message.success('Utente creato con successo')
      }

      setIsModalOpen(false)
      setEditingUser(null)
      loadUsers()
    } catch (error) {
      console.error('Errore:', error)
      message.error('Errore durante il salvataggio dell\'utente')
    }
  }

  const columns: ColumnsType<User> = [
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: 'Nome Completo',
      dataIndex: 'nome',
      key: 'nome',
      render: (_text: any, record: any) => `${record.nome} ${record.cognome}`,
      width: 150,
    },
    {
      title: 'Ruolo',
      dataIndex: 'ruolo',
      key: 'ruolo',
      width: 120,
      render: (ruolo: string) => {
        const ruoloMap: { [key: string]: string } = {
          'ADMIN': 'Amministratore',
          'GENERAL_MANAGER': 'GM - Direttore',
          'WORKSHOP': 'CMM - Meccanica',
          'BODYSHOP': 'CBM - Carrozzeria'
        }
        return ruoloMap[ruolo] || ruolo
      }
    },
    {
      title: 'Attivo',
      dataIndex: 'attivo',
      key: 'attivo',
      width: 80,
      render: (attivo: boolean) => attivo ? '✅ Sì' : '❌ No'
    },
    {
      title: 'Azioni',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          />
          <Popconfirm
            title="Eliminare utente?"
            description="Questa azione non può essere annullata"
            onConfirm={() => handleDelete(record.id)}
            okText="Sì"
            cancelText="No"
          >
            <Button danger size="small" icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  console.log('📊 SettingsPage render - isModalOpen:', isModalOpen, 'editingUser:', editingUser?.email)

  return (
    <div style={{ padding: '24px' }}>
      <PageHeader title="⚙️ Impostazioni Sistema" />

      <Tabs
        items={[
          {
            key: 'users',
            label: '👥 Gestione Utenze',
            children: (
              <Card style={{ marginTop: 20 }}>
                <Block title="Gestione Utenti Applicazione">
                  <div style={{ marginBottom: 20 }}>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={handleCreate}
                    >
                      Aggiungi Utente
                    </Button>
                  </div>

                  <Table
                    columns={columns}
                    dataSource={users}
                    loading={loading}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                  />
                </Block>
              </Card>
            )
          },
          {
            key: 'lookup',
            label: '📋 Tabelle di Sistema',
            children: (
              <Card style={{ marginTop: 20 }}>
                <Tabs
                  defaultActiveKey="damage-types"
                  items={[
                    {
                      key: 'damage-types',
                      label: '🔧 Tipi di Danno',
                      children: (
                        <SystemTableManager
                          title="Tipo di Danno"
                          endpoint={API_ENDPOINTS.SYSTEM_DAMAGE_TYPES}
                          columns={[
                            {
                              title: 'Nome',
                              dataIndex: 'nome',
                              key: 'nome',
                              width: 150,
                            },
                            {
                              title: 'Descrizione',
                              dataIndex: 'descrizione',
                              key: 'descrizione',
                              ellipsis: true,
                            },
                            {
                              title: 'Attivo',
                              dataIndex: 'attivo',
                              key: 'attivo',
                              width: 80,
                              render: (attivo: boolean) => attivo ? '✅' : '❌'
                            }
                          ]}
                        />
                      )
                    },
                    {
                      key: 'customer-types',
                      label: '👤 Tipi di Cliente',
                      children: (
                        <SystemTableManager
                          title="Tipo di Cliente"
                          endpoint={API_ENDPOINTS.SYSTEM_CUSTOMER_TYPES}
                          columns={[
                            {
                              title: 'Nome',
                              dataIndex: 'nome',
                              key: 'nome',
                              width: 150,
                            },
                            {
                              title: 'Descrizione',
                              dataIndex: 'descrizione',
                              key: 'descrizione',
                              ellipsis: true,
                            },
                            {
                              title: 'Attivo',
                              dataIndex: 'attivo',
                              key: 'attivo',
                              width: 80,
                              render: (attivo: boolean) => attivo ? '✅' : '❌'
                            }
                          ]}
                        />
                      )
                    },
                    {
                      key: 'status-types',
                      label: '📊 Stati Scheda Lavori',
                      children: (
                        <SystemTableManager
                          title="Stato Scheda"
                          endpoint={API_ENDPOINTS.SYSTEM_WORKORDER_STATUS_TYPES}
                          columns={[
                            {
                              title: 'Nome',
                              dataIndex: 'nome',
                              key: 'nome',
                              width: 150,
                            },
                            {
                              title: 'Descrizione',
                              dataIndex: 'descrizione',
                              key: 'descrizione',
                              ellipsis: true,
                            },
                            {
                              title: 'Attivo',
                              dataIndex: 'attivo',
                              key: 'attivo',
                              width: 80,
                              render: (attivo: boolean) => attivo ? '✅' : '❌'
                            }
                          ]}
                        />
                      )
                    },
                    {
                      key: 'priority-types',
                      label: '⚡ Priorità',
                      children: (
                        <SystemTableManager
                          title="Priorità"
                          endpoint={API_ENDPOINTS.SYSTEM_PRIORITY_TYPES}
                          columns={[
                            {
                              title: 'Nome',
                              dataIndex: 'nome',
                              key: 'nome',
                              width: 150,
                            },
                            {
                              title: 'Descrizione',
                              dataIndex: 'descrizione',
                              key: 'descrizione',
                              ellipsis: true,
                            },
                            {
                              title: 'Attivo',
                              dataIndex: 'attivo',
                              key: 'attivo',
                              width: 80,
                              render: (attivo: boolean) => attivo ? '✅' : '❌'
                            }
                          ]}
                        />
                      )
                    },
                    {
                      key: 'intervention-status-types',
                      label: '🔩 Stati Intervento',
                      children: (
                        <InterventionStatusTypeManager
                          title="Stato Intervento"
                          endpoint={API_ENDPOINTS.SYSTEM_INTERVENTION_STATUS_TYPES}
                        />
                      )
                    }
                  ]}
                />
              </Card>
            )
          }
        ]}
      />

      {/* User Form Modal */}
      <UserFormModal
        open={isModalOpen}
        editingUser={editingUser}
        onOk={handleModalOkValues}
        onCancel={() => {
          setIsModalOpen(false)
          setEditingUser(null)
        }}
        loading={false}
      />
    </div>
  )
}

// Helper component
const Block = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div style={{ marginBottom: 24 }}>
    <h3 style={{ marginBottom: 16, fontSize: 16, fontWeight: 600 }}>
      {title}
    </h3>
    {children}
  </div>
)

export default SettingsPage
