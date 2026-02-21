import React, { useEffect, useState, useMemo } from 'react'
import { Table, Select, Spin, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'

interface User {
  id: number
  email: string
  username: string
  nome: string
  cognome: string
  ruolo: string
  workshop_id?: number
  attivo: boolean
}

const RUOLI = [
  { label: '👑 Admin', value: 'ADMIN', color: '#f5222d' },
  { label: '🏢 General Manager', value: 'GENERAL_MANAGER', color: '#1890ff' },
  { label: '👤 GM Assistant', value: 'GM_ASSISTANT', color: '#2f54eb' },
  { label: '🖥️ Frontend Manager', value: 'FRONTEND_MANAGER', color: '#fa541c' },
  { label: '🔧 Capo Meccanica', value: 'CMM', color: '#52c41a' },
  { label: '🎨 Capo Carrozzeria', value: 'CBM', color: '#722ed1' },
  { label: '🔨 Operatore Meccanica', value: 'WORKSHOP', color: '#13c2c2' },
  { label: '🎨 Operatore Carrozzeria', value: 'BODYSHOP', color: '#eb2f96' },
]

const UsersManager: React.FC = () => {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get(API_ENDPOINTS.USERS)
      setUsers(response.data.items || response.data._items || response.data || [])
    } catch (error) {
      message.error('Errore nel caricamento degli utenti')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const updateUserRole = async (userId: number, newRole: string) => {
    try {
      await axiosInstance.patch(`${API_ENDPOINTS.USERS}${userId}`, { ruolo: newRole })
      message.success('Ruolo aggiornato')
      setUsers(users.map(u => u.id === userId ? { ...u, ruolo: newRole } : u))
    } catch (error) {
      message.error('Errore aggiornamento ruolo')
      console.error(error)
    }
  }

  const columns: ColumnsType<User> = useMemo(() => [
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      width: 200,
      render: (text: string) => <code style={{ fontSize: '11px' }}>{text}</code>,
    },
    {
      title: 'Utente',
      dataIndex: 'nome',
      key: 'nome',
      width: 140,
      render: (text: string, record: User) => `${text} ${record.cognome}`,
    },
    {
      title: 'Ruolo',
      dataIndex: 'ruolo',
      key: 'ruolo',
      width: 200,
      render: (ruolo: string, record: User) => (
        <Select
          value={ruolo}
          onChange={(newRole) => updateUserRole(record.id, newRole)}
          options={RUOLI.map(r => ({ label: r.label, value: r.value }))}
          size="small"
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: 'Status',
      dataIndex: 'attivo',
      key: 'attivo',
      width: 90,
      align: 'center' as const,
      render: (attivo: boolean) => (
        <span style={{ fontSize: '12px', fontWeight: 500 }}>
          {attivo ? '✅ Attivo' : '⏸️ Inattivo'}
        </span>
      ),
    },
  ], [])

  return (
    <div>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          pagination={{ pageSize: 15 }}
          bordered
          size="small"
        />
      </Spin>
    </div>
  )
}

export default UsersManager
