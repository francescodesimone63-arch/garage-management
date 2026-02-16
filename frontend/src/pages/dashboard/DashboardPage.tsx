import { Card, Row, Col, Statistic, Typography, Space, Spin, Empty, Alert } from 'antd'
import {
  CarOutlined,
  UserOutlined,
  ToolOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { DashboardSummary } from '@/types'

const { Title } = Typography

const DashboardPage = () => {
  const { data: summary, isLoading, error } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: async () => {
      const response = await axiosInstance.get<DashboardSummary>(
        API_ENDPOINTS.DASHBOARD_SUMMARY
      )
      return response.data
    },
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minuti
  })

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Caricamento dashboard..." />
      </div>
    )
  }

  if (error) {
    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Title level={2}>Dashboard</Title>
        <Alert
          message="Errore caricamento dashboard"
          description={(error as any).message || "Non è possibile caricare i dati del dashboard. Prova a ricaricare la pagina."
          }
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

export default DashboardPage
