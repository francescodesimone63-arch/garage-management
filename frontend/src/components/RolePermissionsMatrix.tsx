import React, { useEffect, useState } from 'react'
import { Table, Button, Checkbox, Space, message, Spin, Divider } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import axiosInstance from '@/lib/axios'

interface Permission {
  id: number
  codice: string
  nome: string
  categoria: string
  descrizione: string
  roles: {
    ruolo: string
    granted: boolean
  }[]
}

export const RolePermissionsMatrix: React.FC = () => {
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [roles, setRoles] = useState<string[]>([])
  const [changes, setChanges] = useState<{[key: string]: boolean}>({})

  useEffect(() => {
    fetchMatrix()
  }, [])

  const fetchMatrix = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get('/permissions/matrix')
      setPermissions(response.data.permissions)
      setRoles(response.data.roles)
      setChanges({})
    } catch (error) {
      message.error('Errore nel caricamento della matrice permessi')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = (permissionId: number, role: string, granted: boolean) => {
    const key = `${role}-${permissionId}`
    setChanges({
      ...changes,
      [key]: !granted,
    })
  }

  const getPermissionValue = (perm: Permission, role: string): boolean => {
    const key = `${role}-${perm.id}`
    if (changes.hasOwnProperty(key)) {
      return changes[key]
    }
    const roleData = perm.roles.find(r => r.ruolo === role)
    return roleData?.granted ?? false
  }

  const saveMatrix = async () => {
    try {
      setSaving(true)

      // Costruisci il payload
      const payload: { [key: string]: { [key: string]: boolean } } = {}

      for (const role of roles) {
        payload[role] = {}
        for (const perm of permissions) {
          const value = getPermissionValue(perm, role)
          payload[role][perm.codice] = value
        }
      }

      await axiosInstance.put('/permissions/matrix', payload)
      message.success('Permessi aggiornati con successo')
      setChanges({})
      await fetchMatrix()
    } catch (error) {
      message.error('Errore nel salvataggio dei permessi')
      console.error(error)
    } finally {
      setSaving(false)
    }
  }

  const hasChanges = Object.keys(changes).length > 0

  // Raggruppa i permessi per categoria
  const permissionsByCategory = permissions.reduce(
    (acc, perm) => {
      if (!acc[perm.categoria]) {
        acc[perm.categoria] = []
      }
      acc[perm.categoria].push(perm)
      return acc
    },
    {} as { [key: string]: Permission[] }
  )

  return (
    <div>
      <div style={{ marginBottom: '12px', display: 'flex', gap: '8px' }}>
        <Button
          icon={<ReloadOutlined />}
          onClick={fetchMatrix}
          loading={loading}
          size="small"
        >
          Ricarica
        </Button>

        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={saveMatrix}
          loading={saving}
          disabled={!hasChanges}
          size="small"
        >
          Salva ({Object.keys(changes).length})
        </Button>
      </div>

      {hasChanges && (
        <div
          style={{
            padding: '8px 12px',
            marginBottom: '12px',
            backgroundColor: '#e6f7ff',
            border: '1px solid #91d5ff',
            borderRadius: '2px',
            color: '#0050b3',
            fontSize: '12px',
          }}
        >
          ⚠️ {Object.keys(changes).length} cambio/i non salvato/i
        </div>
      )}

      <Spin spinning={loading}>
        {Object.entries(permissionsByCategory).map(([category, categoryPerms]) => (
          <div key={category} style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, marginBottom: '8px', color: '#1890ff' }}>
              {category} ({categoryPerms.length})
            </div>

            <div
              style={{
                overflowX: 'auto',
                border: '1px solid #d9d9d9',
              }}
            >
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '12px',
                }}
              >
                <thead>
                  <tr style={{ backgroundColor: '#fafafa', borderBottom: '1px solid #d9d9d9' }}>
                    <th style={{ padding: '6px 8px', textAlign: 'left', fontWeight: 600, borderRight: '1px solid #d9d9d9' }}>
                      Permesso
                    </th>
                    {roles.map((role) => (
                      <th
                        key={role}
                        style={{
                          padding: '6px 4px',
                          textAlign: 'center',
                          fontWeight: 600,
                          whiteSpace: 'nowrap',
                          minWidth: '60px',
                          borderRight: '1px solid #d9d9d9',
                          fontSize: '11px',
                        }}
                      >
                        {role.substring(0, 6)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {categoryPerms.map((perm) => (
                    <tr
                      key={perm.id}
                      style={{
                        borderBottom: '1px solid #f0f0f0',
                      }}
                    >
                      <td style={{ padding: '6px 8px', textAlign: 'left', borderRight: '1px solid #d9d9d9', fontSize: '11px' }}>
                        <div style={{ fontWeight: 500 }}>{perm.nome}</div>
                      </td>

                      {roles.map((role) => {
                        const isGranted = getPermissionValue(perm, role)
                        const isChanged = changes.hasOwnProperty(`${role}-${perm.id}`)

                        return (
                          <td
                            key={role}
                            style={{
                              padding: '4px',
                              textAlign: 'center',
                              backgroundColor: isChanged ? '#e6f7ff' : 'transparent',
                              borderRight: '1px solid #d9d9d9',
                            }}
                          >
                            <Checkbox
                              checked={isGranted}
                              onChange={() =>
                                handleToggle(perm.id, role, isGranted)
                              }
                            />
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </Spin>
    </div>
  )
}

export default RolePermissionsMatrix
