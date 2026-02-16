import { Modal } from 'antd'
import { ExclamationCircleOutlined } from '@ant-design/icons'

const { confirm } = Modal

interface ConfirmModalProps {
  title: string
  content: string
  onOk: () => void | Promise<void>
  okText?: string
  cancelText?: string
  okType?: 'primary' | 'danger'
}

export const showConfirm = ({
  title,
  content,
  onOk,
  okText = 'Conferma',
  cancelText = 'Annulla',
  okType = 'primary',
}: ConfirmModalProps) => {
  confirm({
    title,
    icon: <ExclamationCircleOutlined />,
    content,
    okText,
    cancelText,
    okType,
    onOk,
  })
}

export const showDeleteConfirm = (
  itemName: string,
  onOk: () => void | Promise<void>
) => {
  showConfirm({
    title: 'Conferma Eliminazione',
    content: `Sei sicuro di voler eliminare ${itemName}?`,
    okText: 'Elimina',
    cancelText: 'Annulla',
    okType: 'danger',
    onOk,
  })
}
