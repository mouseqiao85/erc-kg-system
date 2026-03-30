import { useState, useEffect } from 'react'
import { Card, Form, InputNumber, Select, Slider, Button, Row, Col, message, Divider, Typography, Space, Input } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'

const { Title, Text } = Typography

interface SystemConfig {
  llm_model: string
  temperature: number
  max_entities: number
  similarity_threshold: number
  alpha: number
  top_k: number
  enable_validation: boolean
  enable_llm_review: boolean
}

const defaultConfig: SystemConfig = {
  llm_model: 'gpt-4',
  temperature: 0.7,
  max_entities: 50,
  similarity_threshold: 0.8,
  alpha: 0.8,
  top_k: 10,
  enable_validation: true,
  enable_llm_review: true,
}

const STORAGE_KEY = 'erc-kg-config'

export default function Settings() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    const savedConfig = localStorage.getItem(STORAGE_KEY)
    if (savedConfig) {
      try {
        const parsed = JSON.parse(savedConfig)
        form.setFieldsValue(parsed)
      } catch {
        form.setFieldsValue(defaultConfig)
      }
    } else {
      form.setFieldsValue(defaultConfig)
    }
  }, [form])

  const handleValuesChange = () => {
    setHasChanges(true)
  }

  const handleSave = async (values: SystemConfig) => {
    setLoading(true)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(values))
      message.success('Settings saved successfully')
      setHasChanges(false)
    } catch (err) {
      message.error('Failed to save settings')
    }
    setLoading(false)
  }

  const handleReset = () => {
    form.setFieldsValue(defaultConfig)
    localStorage.removeItem(STORAGE_KEY)
    message.success('Settings reset to default')
    setHasChanges(true)
  }

  const llmModels = [
    { label: 'GPT-4', value: 'gpt-4' },
    { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
    { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
    { label: 'Claude-3 Opus', value: 'claude-3-opus' },
    { label: 'Claude-3 Sonnet', value: 'claude-3-sonnet' },
  ]

  return (
    <div>
      <Title level={4}>System Settings</Title>
      <Text type="secondary">Configure LLM parameters and knowledge graph extraction settings</Text>
      
      <Divider />

      <Card style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onValuesChange={handleValuesChange}
          onFinish={handleSave}
          initialValues={defaultConfig}
        >
          <Row gutter={24}>
            <Col span={12}>
              <Title level={5}>LLM Configuration</Title>
              
              <Form.Item
                name="llm_model"
                label="LLM Model"
                tooltip="Select the language model for knowledge extraction"
              >
                <Select options={llmModels} />
              </Form.Item>

              <Form.Item
                name="temperature"
                label="Temperature"
                tooltip="Controls randomness (0 = deterministic, 1 = creative)"
              >
                <Slider
                  min={0}
                  max={1}
                  step={0.1}
                  marks={{ 0: '0', 0.5: '0.5', 1: '1' }}
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Title level={5}>Extraction Parameters</Title>
              
              <Form.Item
                name="max_entities"
                label="Max Entities"
                tooltip="Maximum number of entities to extract from documents"
              >
                <InputNumber min={1} max={500} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="similarity_threshold"
                label="Similarity Threshold"
                tooltip="Minimum similarity score for entity matching"
              >
                <Slider
                  min={0}
                  max={1}
                  step={0.1}
                  marks={{ 0: '0', 0.5: '0.5', 1: '1' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col span={12}>
              <Title level={5}>Retrieval Settings</Title>
              
              <Form.Item
                name="alpha"
                label="Alpha (Retrieval Weight)"
                tooltip="Weight for similarity-based retrieval vs keyword matching"
              >
                <Slider
                  min={0}
                  max={1}
                  step={0.1}
                  marks={{ 0: '0', 0.5: '0.5', 1: '1' }}
                />
              </Form.Item>

              <Form.Item
                name="top_k"
                label="Top K"
                tooltip="Number of top results to retrieve"
              >
                <InputNumber min={1} max={50} style={{ width: '100%' }} />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Title level={5}>Validation Settings</Title>
              
              <Form.Item
                name="enable_validation"
                label="Enable Validation"
                tooltip="Enable triple validation after extraction"
                valuePropName="checked"
              >
                <Select
                  options={[
                    { label: 'Enabled', value: true },
                    { label: 'Disabled', value: false },
                  ]}
                />
              </Form.Item>

              <Form.Item
                name="enable_llm_review"
                label="Enable LLM Review"
                tooltip="Use LLM for secondary validation"
                valuePropName="checked"
              >
                <Select
                  options={[
                    { label: 'Enabled', value: true },
                    { label: 'Disabled', value: false },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>

          <Divider />

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
                Save Settings
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                Reset to Default
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card title="API Configuration">
        <Row gutter={16}>
          <Col span={12}>
            <Text strong>API Endpoint:</Text>
            <Input value="/api/v1" disabled style={{ marginTop: 8 }} />
          </Col>
          <Col span={12}>
            <Text strong>WebSocket:</Text>
            <Input value="ws://host/api/v1/ws/jobs/:jobId" disabled style={{ marginTop: 8 }} />
          </Col>
        </Row>
      </Card>

      {hasChanges && (
        <div style={{ marginTop: 16, padding: 16, background: '#fffbe6', borderRadius: 4 }}>
          <Text type="warning">You have unsaved changes. Click "Save Settings" to apply.</Text>
        </div>
      )}
    </div>
  )
}
