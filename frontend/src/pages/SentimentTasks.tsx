import { useState, useEffect } from 'react'
import { Card, Table, Button, Space, Tag, Progress, Modal, Form, Input, InputNumber, Select, message, Descriptions, List, Statistic, Row, Col, Alert } from 'antd'
import { PlayCircleOutlined, ReloadOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import { useState as useReactState } from 'react'

interface Task {
  id: string
  name: string
  status: string
  progress: number
  config: any
  result: any
  error_message: string
  created_at: string
  started_at: string
  completed_at: string
}

export default function SentimentTasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [form] = Form.useForm()

  const fetchTasks = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/tasks')
      const data = await res.json()
      setTasks(data.items || [])
    } catch (err) {
      message.error('Failed to fetch tasks')
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchTasks()
    const interval = setInterval(fetchTasks, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleCreate = async (values: any) => {
    try {
      const res = await fetch('/api/v1/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      })
      
      if (res.ok) {
        message.success('Task created')
        setCreateModalVisible(false)
        form.resetFields()
        fetchTasks()
      } else {
        message.error('Failed to create task')
      }
    } catch (err) {
      message.error('Failed to create task')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await fetch(`/api/v1/tasks/${id}`, { method: 'DELETE' })
      message.success('Task deleted')
      fetchTasks()
    } catch (err) {
      message.error('Failed to delete task')
    }
  }

  const showDetail = (task: Task) => {
    setSelectedTask(task)
    setDetailModalVisible(true)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green'
      case 'running': return 'blue'
      case 'failed': return 'red'
      default: return 'default'
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', render: (id: string) => id?.slice(0, 8) },
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => <Tag color={getStatusColor(status)}>{status}</Tag>
    },
    { title: 'Progress', dataIndex: 'progress', key: 'progress', render: (p: number) => <Progress percent={p || 0} size="small" /> },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at', render: (t: string) => new Date(t).toLocaleString() },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Task) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />} onClick={() => showDetail(record)}>View</Button>
          <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>Delete</Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      <Alert 
        message="舆情分析任务流程" 
        description="1. 创建任务 → 2. 互联网搜索获取舆情数据 → 3. 构建知识图谱 → 4. 四维舆情评分"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Card 
        title="Sentiment Analysis Tasks"
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchTasks}>Refresh</Button>
            <Button type="primary" icon={<PlayCircleOutlined />} onClick={() => setCreateModalVisible(true)}>
              Create Task
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="Create Sentiment Task"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="Task Name" rules={[{ required: true }]}>
            <Input placeholder="Enter task name" />
          </Form.Item>
          <Form.Item name="entity_name" label="Entity Name" rules={[{ required: true }]}>
            <Input placeholder="Enter entity name to analyze" />
          </Form.Item>
          <Form.Item name="keywords" label="Additional Keywords">
            <Select mode="tags" placeholder="Add keywords" />
          </Form.Item>
          <Form.Item name="days" label="Search Days" initialValue={30}>
            <InputNumber min={1} max={90} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Start Task
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Task Details"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedTask && (
          <div>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="ID">{selectedTask.id}</Descriptions.Item>
              <Descriptions.Item label="Name">{selectedTask.name}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={getStatusColor(selectedTask.status)}>{selectedTask.status}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Progress">
                <Progress percent={selectedTask.progress || 0} />
              </Descriptions.Item>
              <Descriptions.Item label="Created">{new Date(selectedTask.created_at).toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="Completed">
                {selectedTask.completed_at ? new Date(selectedTask.completed_at).toLocaleString() : '-'}
              </Descriptions.Item>
            </Descriptions>

            {selectedTask.result && (
              <Card title="Result" style={{ marginTop: 16 }}>
                <Row gutter={16}>
                  <Col span={6}>
                    <Statistic title="Sentiment Score" value={selectedTask.result.sentiment_score} precision={2} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="Trend" value={selectedTask.result.trend} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="Risk Level" value={selectedTask.result.risk_level} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="Articles" value={selectedTask.result.articles_count} />
                  </Col>
                </Row>
              </Card>
            )}

            {selectedTask.error_message && (
              <Alert 
                message="Error" 
                description={selectedTask.error_message} 
                type="error" 
                style={{ marginTop: 16 }}
              />
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
