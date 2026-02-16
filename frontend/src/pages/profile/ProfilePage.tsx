import { Typography, Card, Descriptions } from 'antd'
import { useAuth } from '@/contexts/AuthContext'

const { Title } = Typography

const ProfilePage = () => {
  const { user } = useAuth()

  return (
    <div>
      <Title level={2}>Profilo Utente</Title>
      <Card>
        <Descriptions column={1}>
          <Descriptions.Item label="Nome completo">
            {user?.nome} {user?.cognome}
          </Descriptions.Item>
          <Descriptions.Item label="Email">{user?.email}</Descriptions.Item>
          <Descriptions.Item label="Ruolo">{user?.ruolo}</Descriptions.Item>
          <Descriptions.Item label="Stato">
            {user?.attivo ? 'Attivo' : 'Non attivo'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  )
}

export default ProfilePage
