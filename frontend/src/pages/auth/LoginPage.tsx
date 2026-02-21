import { useState, useEffect } from 'react'
import { Card, Form, Input, Button, Typography, Space, Alert } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useAuth } from '@/contexts/AuthContext'
import type { LoginRequest } from '@/types'

const { Title, Text } = Typography

const LoginPage = () => {
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const [form] = Form.useForm()
  const [debugInfo, setDebugInfo] = useState<string>('')

  useEffect(() => {
    console.log('✅ LoginPage component mounted')
    setDebugInfo('Component loaded. Click Accedi to login.')
  }, [])

  const onFinish = async (values: LoginRequest) => {
    try {
      const msg = `🔐 Form submitted: ${values.username}`
      console.log(msg)
      setDebugInfo(msg)
      setLoading(true)
      
      console.log('📝 Calling login function...')
      setDebugInfo(prev => prev + '\n📝 Calling login function...')
      
      await login(values)
      
      console.log('✅ Login completed successfully')
      setDebugInfo(prev => prev + '\n✅ Login completed successfully')
    } catch (error: any) {
      const errMsg = `❌ Login error: ${error?.message || error}`
      console.error(errMsg)
      setDebugInfo(prev => prev + `\n${errMsg}`)
    } finally {
      setLoading(false)
    }
  }

  const onFinishFailed = (errorInfo: any) => {
    console.error('❌ Form validation failed:', errorInfo)
    setDebugInfo(`Form validation failed: ${JSON.stringify(errorInfo)}`)
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              Garage Management
            </Title>
            <Text type="secondary">Accedi al tuo account</Text>
          </div>

          <Form
            form={form}
            name="login"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            layout="vertical"
            size="large"
            initialValues={{
              username: 'admin',
              password: 'admin123',
            }}
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: 'Inserisci il tuo username' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Username"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Inserisci la password' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
                onClick={() => {
                  console.log('🔘 Button clicked')
                  setDebugInfo('🔘 Button clicked - preparing to submit...')
                }}
              >
                Accedi
              </Button>
            </Form.Item>
          </Form>

          {debugInfo && (
            <Alert
              message="Debug Info"
              description={debugInfo}
              type="info"
              showIcon
              style={{ whiteSpace: 'pre-wrap', fontSize: '11px', maxHeight: '150px', overflow: 'auto' }}
            />
          )}

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              © 2026 Garage Management System v1.0.0
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  )
}

export default LoginPage
