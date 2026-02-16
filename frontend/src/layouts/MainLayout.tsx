import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Layout,
  Menu,
  Avatar,
  Dropdown,
  Badge,
  theme,
  Typography,
} from 'antd'
import type { MenuProps } from 'antd'
import {
  DashboardOutlined,
  UserOutlined,
  CarOutlined,
  ToolOutlined,
  ShoppingOutlined,
  CarryOutOutlined,
  BellOutlined,
  CalendarOutlined,
  LogoutOutlined,
  SettingOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import { useAuth } from '@/contexts/AuthContext'
import { UserRole } from '@/types'

const { Header, Sider, Content } = Layout
const { Text } = Typography

const MainLayout = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  const { token } = theme.useToken()

  // Debug: stampa il ruolo dell'utente
  console.log('🔍 MainLayout - User ruolo:', user?.ruolo)
  console.log('🔍 MainLayout - Is ADMIN:', user?.ruolo === UserRole.ADMIN)
  console.log('🔍 MainLayout - UserRole.ADMIN value:', UserRole.ADMIN)

  // Menu items basati sul ruolo
  const getMenuItems = (): MenuProps['items'] => {
    const baseItems: MenuProps['items'] = [
      {
        key: '/dashboard',
        icon: <DashboardOutlined />,
        label: 'Dashboard',
      },
    ]

    // Items per tutti i ruoli autenticati
    const commonItems: MenuProps['items'] = [
      {
        key: '/customers',
        icon: <TeamOutlined />,
        label: 'Clienti',
      },
      {
        key: '/vehicles',
        icon: <CarOutlined />,
        label: 'Veicoli',
      },
      {
        key: '/work-orders',
        icon: <ToolOutlined />,
        label: 'Ordini di Lavoro',
      },
      {
        key: '/calendar',
        icon: <CalendarOutlined />,
        label: 'Calendario',
      },
    ]

    // Items aggiuntivi per officina/carrozzeria
    const workshopItems: MenuProps['items'] = [
      {
        key: '/parts',
        icon: <ShoppingOutlined />,
        label: 'Ricambi',
      },
      {
        key: '/tires',
        icon: <CarryOutOutlined />,
        label: 'Pneumatici',
      },
      {
        key: '/courtesy-cars',
        icon: <CarOutlined />,
        label: 'Auto Cortesia',
      },
      {
        key: '/maintenance',
        icon: <ToolOutlined />,
        label: 'Manutenzioni',
      },
    ]

    // Items per admin
    const adminItems: MenuProps['items'] = [
      {
        key: '/users',
        icon: <UserOutlined />,
        label: 'Utenti',
      },
    ]

    let items = [...baseItems, ...commonItems]

    if (user?.ruolo === UserRole.ADMIN || user?.ruolo === UserRole.GENERAL_MANAGER) {
      items = [...items, ...workshopItems, ...adminItems]
    } else if (
      user?.ruolo === UserRole.WORKSHOP ||
      user?.ruolo === UserRole.BODYSHOP
    ) {
      items = [...items, ...workshopItems]
    }

    return items
  }

  // Dropdown menu per utente
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profilo',
      onClick: () => navigate('/profile'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: logout,
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="light"
        style={{
          borderRight: `1px solid ${token.colorBorder}`,
        }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderBottom: `1px solid ${token.colorBorder}`,
            padding: '0 16px',
          }}
        >
          <ToolOutlined style={{ fontSize: 24, color: token.colorPrimary }} />
          {!collapsed && (
            <Text strong style={{ marginLeft: 12, fontSize: 16 }}>
              Garage
            </Text>
          )}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={getMenuItems()}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>

      <Layout>
        <Header
          style={{
            padding: '0 24px',
            background: token.colorBgContainer,
            borderBottom: `1px solid ${token.colorBorder}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div />
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            {/* Notifiche */}
            <Badge count={0} showZero={false}>
              <BellOutlined
                style={{ fontSize: 20, cursor: 'pointer' }}
                onClick={() => navigate('/notifications')}
              />
            </Badge>

            {/* Impostazioni (solo ADMIN) */}
            {user?.ruolo === UserRole.ADMIN && (
              <>
                <div
                  onClick={() => {
                    console.log('⚙️ Settings icon clicked!')
                    navigate('/settings')
                  }}
                  style={{
                    fontSize: 20,
                    cursor: 'pointer',
                    color: token.colorPrimary,
                    padding: '8px',
                    borderRadius: '4px',
                    transition: 'background 0.3s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = token.colorPrimaryBgHover
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent'
                  }}
                  title="⚙️ Impostazioni Sistema"
                >
                  <SettingOutlined />
                </div>
              </>
            )}

            {/* Menu utente */}
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <Text style={{ marginLeft: 8 }}>{user?.nome} {user?.cognome}</Text>
              </div>
            </Dropdown>
          </div>
        </Header>

        <Content
          style={{
            margin: 24,
            minHeight: 280,
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
