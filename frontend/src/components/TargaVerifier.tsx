import { useState } from 'react'
import { Input, Button, Select, Space, Row, Col, Spin, Alert, Tooltip, Typography, Divider } from 'antd'
import { SearchOutlined, CarOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { useMarche, useModelli, useVerificaTarga, useCarburanti } from '@/hooks/useAuto'
import type { DatiTargaResponse } from '@/types'
import type { FormInstance } from 'antd'

const { Text } = Typography

interface TargaVerifierProps {
  form: FormInstance
  /** Callback chiamato quando i dati vengono popolati dalla verifica targa */
  onDataFilled?: (data: DatiTargaResponse) => void
  /** Modalità: 'create' mostra tutti i campi, 'search' solo la targa */
  mode?: 'create' | 'search'
}

/**
 * Componente per la verifica della targa e selezione marca/modello
 * Si integra con Ant Design Form per popolare automaticamente i campi
 */
const TargaVerifier: React.FC<TargaVerifierProps> = ({ form, onDataFilled, mode = 'create' }) => {
  const [selectedMarca, setSelectedMarca] = useState<string>('')
  const [lastVerifiedTarga, setLastVerifiedTarga] = useState<string>('')

  // Hooks per i dati
  const { data: marcheData, isLoading: loadingMarche } = useMarche()
  const { data: modelliData, isLoading: loadingModelli } = useModelli(selectedMarca)
  const { data: carburanti } = useCarburanti()
  const verificaTarga = useVerificaTarga()

  // Gestione selezione marca
  const handleMarcaChange = (value: string) => {
    setSelectedMarca(value)
    // Reset modello quando cambia la marca
    form.setFieldValue('modello', undefined)
  }

  // Verifica targa e popola i campi
  const handleVerificaTarga = async () => {
    const targa = form.getFieldValue('targa')
    if (!targa || targa.length < 5) {
      return
    }

    try {
      const data = await verificaTarga.mutateAsync(targa)
      
      // Popola i campi del form
      form.setFieldsValue({
        marca: data.marca,
        modello: data.modello,
        anno: data.anno,
        colore: data.colore || undefined,
        telaio: data.telaio || undefined,
        cilindrata: data.cilindrata || undefined,
        kw: data.kw || undefined,
        cv: data.cv || undefined,
        porte: data.porte || undefined,
        carburante: data.carburante || undefined,
        prima_immatricolazione: data.prima_immatricolazione || undefined,
      })

      // Aggiorna la marca selezionata per il dropdown modelli
      setSelectedMarca(data.marca)
      setLastVerifiedTarga(targa.toUpperCase())

      // Notifica il parent
      if (onDataFilled) {
        onDataFilled(data)
      }
    } catch (error) {
      // L'errore è gestito dal mutation hook
      console.error('Errore verifica targa:', error)
    }
  }

  // Gestione blur sulla targa
  const handleTargaBlur = () => {
    const targa = form.getFieldValue('targa')?.toUpperCase().replace(/\s/g, '')
    if (targa && targa.length >= 7 && targa !== lastVerifiedTarga) {
      // Auto-verifica quando la targa cambia
      handleVerificaTarga()
    }
  }

  if (mode === 'search') {
    return (
      <Space.Compact style={{ width: '100%' }}>
        <Input
          placeholder="Inserisci targa (es. AB123CD)"
          onBlur={handleTargaBlur}
          onChange={(e) => form.setFieldValue('targa', e.target.value.toUpperCase())}
          prefix={<CarOutlined />}
        />
        <Button
          type="primary"
          icon={<SearchOutlined />}
          onClick={handleVerificaTarga}
          loading={verificaTarga.isPending}
        >
          Cerca
        </Button>
      </Space.Compact>
    )
  }

  return (
    <div>
      {/* Sezione Targa con verifica */}
      <Row gutter={16} align="middle">
        <Col span={16}>
          <div style={{ marginBottom: 8 }}>
            <Text strong>
              <CarOutlined /> Targa
            </Text>
            <Tooltip title="Inserisci la targa per auto-compilare i dati del veicolo">
              <InfoCircleOutlined style={{ marginLeft: 8, color: '#1890ff' }} />
            </Tooltip>
          </div>
        </Col>
      </Row>

      {verificaTarga.isError && (
        <Alert
          message="Targa non trovata"
          description="Compila manualmente i dati del veicolo"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {verificaTarga.isSuccess && lastVerifiedTarga && (
        <Alert
          message={`Dati auto-compilati per targa ${lastVerifiedTarga}`}
          type="success"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      <Divider orientation="left" style={{ marginTop: 24 }}>
        <CarOutlined /> Marca e Modello
      </Divider>

      {/* Selettori Marca/Modello a cascata */}
      <Row gutter={16}>
        <Col span={12}>
          <div style={{ marginBottom: 8 }}>
            <Text strong>Marca *</Text>
          </div>
          <Select
            showSearch
            placeholder="Seleziona marca"
            value={selectedMarca || form.getFieldValue('marca')}
            onChange={handleMarcaChange}
            loading={loadingMarche}
            optionFilterProp="children"
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            style={{ width: '100%' }}
            options={marcheData?.marche.map((marca) => ({
              value: marca,
              label: marca,
            }))}
            notFoundContent={loadingMarche ? <Spin size="small" /> : 'Nessuna marca trovata'}
          />
        </Col>
        <Col span={12}>
          <div style={{ marginBottom: 8 }}>
            <Text strong>Modello *</Text>
          </div>
          <Select
            showSearch
            placeholder={selectedMarca ? 'Seleziona modello' : 'Prima seleziona la marca'}
            value={form.getFieldValue('modello')}
            onChange={(value) => form.setFieldValue('modello', value)}
            disabled={!selectedMarca}
            loading={loadingModelli}
            optionFilterProp="children"
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            style={{ width: '100%' }}
            options={modelliData?.modelli.map((modello) => ({
              value: modello,
              label: modello,
            }))}
            notFoundContent={
              loadingModelli ? (
                <Spin size="small" />
              ) : selectedMarca ? (
                'Nessun modello trovato'
              ) : (
                'Seleziona prima una marca'
              )
            }
          />
        </Col>
      </Row>

      <Divider orientation="left" style={{ marginTop: 24 }}>
        Dati Tecnici
      </Divider>

      {/* Campi tecnici aggiuntivi */}
      <Row gutter={16}>
        <Col span={6}>
          <div style={{ marginBottom: 8 }}>
            <Text>Carburante</Text>
          </div>
          <Select
            placeholder="Tipo"
            value={form.getFieldValue('carburante')}
            onChange={(value) => form.setFieldValue('carburante', value)}
            style={{ width: '100%' }}
            allowClear
            options={carburanti?.map((c) => ({ value: c, label: c }))}
          />
        </Col>
        <Col span={6}>
          <div style={{ marginBottom: 8 }}>
            <Text>Cilindrata</Text>
          </div>
          <Input
            placeholder="es. 1598 cc"
            value={form.getFieldValue('cilindrata')}
            onChange={(e) => form.setFieldValue('cilindrata', e.target.value)}
          />
        </Col>
        <Col span={6}>
          <div style={{ marginBottom: 8 }}>
            <Text>KW</Text>
          </div>
          <Input
            type="number"
            placeholder="es. 90"
            value={form.getFieldValue('kw')}
            onChange={(e) => form.setFieldValue('kw', e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </Col>
        <Col span={6}>
          <div style={{ marginBottom: 8 }}>
            <Text>CV</Text>
          </div>
          <Input
            type="number"
            placeholder="es. 122"
            value={form.getFieldValue('cv')}
            onChange={(e) => form.setFieldValue('cv', e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={6}>
          <div style={{ marginBottom: 8 }}>
            <Text>N° Porte</Text>
          </div>
          <Select
            placeholder="Porte"
            value={form.getFieldValue('porte')}
            onChange={(value) => form.setFieldValue('porte', value)}
            style={{ width: '100%' }}
            allowClear
            options={[
              { value: 2, label: '2' },
              { value: 3, label: '3' },
              { value: 4, label: '4' },
              { value: 5, label: '5' },
            ]}
          />
        </Col>
        <Col span={9}>
          <div style={{ marginBottom: 8 }}>
            <Text>Prima Immatricolazione</Text>
          </div>
          <Input
            type="date"
            value={form.getFieldValue('prima_immatricolazione')}
            onChange={(e) => form.setFieldValue('prima_immatricolazione', e.target.value)}
          />
        </Col>
      </Row>
    </div>
  )
}

export default TargaVerifier
