import { useState, useEffect } from 'react'
import { Table, Button, Space, Modal, Form, Input, message, Card, Row, Col, Statistic } from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import { projectService } from '../services/api'

interface Project {
  id: string
  name: string
  description: string
  created_at: string
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const res = await projectService.getProjects()
      setProjects(res.data.items || [])
    } catch (err) {
      message.error('Failed to fetch projects')
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  const handleCreate = async (values: { name: string; description: string }) => {
    try {
      await projectService.createProject(values)
      message.success('Project created')
      setModalOpen(false)
      form.resetFields()
      fetchProjects()
    } catch (err) {
      message.error('Failed to create project')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await projectService.deleteProject(id)
      message.success('Project deleted')
      fetchProjects()
    } catch (err) {
      message.error('Failed to delete project')
    }
  }

  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Description', dataIndex: 'description', key: 'description' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at', render: (t: string) => new Date(t).toLocaleString() },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: Project) => (
        <Space>
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>
            Delete
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card><Statistic title="Total Projects" value={projects.length} /></Card>
        </Col>
      </Row>

      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          New Project
        </Button>
      </div>

      <Table columns={columns} dataSource={projects} rowKey="id" loading={loading} />

      <Modal title="New Project" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={form.submit}>
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
