import { Card, Row, Col, Statistic, Typography, Space, Spin, Empty, Alert, Divider, List, Tag } from 'antd'
import {
  CarOutlined,
  UserOutlined,
  ToolOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FileTextOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import { useAuth } from '@/contexts/AuthContext'
import { useCMMStats } from '@/hooks/useCMM'
import type { DashboardSummary, CMMDashboardStats } from '@/types'

const { Title, Text } = Typography

// Colori per gli stati intervento
const statusColors: Record<string, string> = {
  preso_in_carico: '#1890ff',
  attesa_componente: '#faad14',
  sospeso: '#ff4d4f',
  concluso: '#52c41a',
}

// Componente per la dashboard CMM
const CMMDashboard = () => {
  const { data: stats, isLoading, error } = useCMMStats()

  if (isLoading) {
    return <Spin fullscreen size="large" tip="Caricamento dashboard CMM..." />
  }

  if (error) {
    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Title level={2}>Dashboard CMM</Title>
        <Alert
          message="Errore caricamento dashboard"
          description={(error as any).message || "Non è possibile caricare i dati del dashboard. Prova a ricaricare la pagina."}
          type="error"
          showIcon
        />
      </Space>
    )
  }

  if (!stats) {
    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Title level={2}>Dashboard CMM</Title>
        <Empty description="Nessun dato disponibile" />
      </Space>
    )
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={2}>Dashboard CMM</Title>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Da Prendere in Carico"
              value={stats.work_orders_approvate}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="In Lavorazione"
              value={stats.work_orders_in_lavorazione}
              prefix={<ToolOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Clienti Totali"
              value={stats.customers_total}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Veicoli Totali"
              value={stats.vehicles_total}
              prefix={<CarOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Statistiche Interventi */}
      <Card 
        title={
          <Space>
            <ClockCircleOutlined />
            <span>Interventi Meccanici</span>
            <Tag color="blue">{stats.interventi_totali}</Tag>
          </Space>
        }
      >
        <Row gutter={[16, 16]}>
          {/* Subtotali per stato */}
          {stats.interventi_per_stato.map((statoStats) => (
            <Col xs={12} sm={8} md={6} key={statoStats.codice}>
              <Card size="small" bordered={false} style={{ background: '#fafafa' }}>
                <Statistic
                  title={statoStats.nome}
                  value={statoStats.totale}
                  valueStyle={{ 
                    color: statusColors[statoStats.codice] || '#595959',
                    fontSize: '20px'
                  }}
                />
              </Card>
            </Col>
          ))}
          {/* Senza stato assegnato */}
          {stats.interventi_senza_stato > 0 && (
            <Col xs={12} sm={8} md={6}>
              <Card size="small" bordered={false} style={{ background: '#fff2e8' }}>
                <Statistic
                  title="Da assegnare"
                  value={stats.interventi_senza_stato}
                  valueStyle={{ color: '#d46b08', fontSize: '20px' }}
                />
              </Card>
            </Col>
          )}
        </Row>
      </Card>
    </Space>
  )
}

// Dashboard generica per altri ruoli
const GeneralDashboard = () => {
  const { data: summary, isLoading, error } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: async () => {
      const response = await axiosInstance.get<DashboardSummary>(
        API_ENDPOINTS.DASHBOARD_SUMMARY
      )
      return response.data
    },
    retry: 1,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return <Spin fullscreen size="large" tip="Caricamento dashboard..." />
  }

  if (error) {
    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Title level={2}>Dashboard</Title>
        <Alert
          message="Errore caricamento dashboard"
          description={(error as any).message || "Non è possibile caricare i dati del dashboard. Prova a ricaricare la pagina."}
          type="error"
          showIcon
        />
        <Empty description="Nessun dato disponibile" />
      </Space>
    )
  }

  if (!summary?.stats) {
    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Title level={2}>Dashboard</Title>
        <Empty description="Nessun dato disponibile" />
      </Space>
    )
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={2}>Dashboard</Title>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Ordini di Lavoro Aperti"
              value={summary?.stats?.work_orders_open || 0}
              prefix={<ToolOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="In Lavorazione"
              value={summary?.stats?.work_orders_in_progress || 0}
              prefix={<ToolOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Clienti Totali"
              value={summary?.stats?.customers_total || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Veicoli Totali"
              value={summary?.stats?.vehicles_total || 0}
              prefix={<CarOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {summary?.stats?.parts_low_stock ? (
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12}>
            <Card>
              <Statistic
                title="Ricambi in Esaurimento"
                value={summary.stats.parts_low_stock}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12}>
            <Card>
              <Statistic
                title="Auto Cortesia Disponibili"
                value={summary.stats.courtesy_cars_available || 0}
                prefix={<CarOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>
      ) : null}
    </Space>
  )
}

const DashboardPage = () => {
  const { user } = useAuth()
  
  // Mostra dashboard specifica per CMM
  if (user?.ruolo === 'CMM') {
    return <CMMDashboard />
  }
  
  // Dashboard generica per altri ruoli
  return <GeneralDashboard />
}

export default DashboardPage
