import { Result, Button } from 'antd'
import { useNavigate } from 'react-router-dom'

const NotFoundPage = () => {
  const navigate = useNavigate()

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <Result
        status="404"
        title="404"
        subTitle="Spiacenti, la pagina che stai cercando non esiste."
        extra={
          <Button type="primary" onClick={() => navigate('/dashboard')}>
            Torna alla Dashboard
          </Button>
        }
      />
    </div>
  )
}

export default NotFoundPage
