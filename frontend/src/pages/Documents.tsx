import { useState, useEffect } from 'react'
import { Table, Button, Space, Upload, message, Select } from 'antd'
import { UploadOutlined, DeleteOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload/interface'
import { documentService, projectService } from '../services/api'

interface Document {
  id: string
  title: string
  format: string
  status: string
  created_at: string
}

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')

  const fetchDocuments = async () => {
    if (!selectedProject) return
    setLoading(true)
    try {
      const res = await documentService.getDocuments({ project_id: selectedProject })
      setDocuments(res.data.items || [])
    } catch (err) {
      message.error('Failed to fetch documents')
    }
    setLoading(false)
  }

  const fetchProjects = async () => {
    try {
      const res = await projectService.getProjects()
      setProjects(res.data.items || [])
      if (res.data.items?.length > 0) {
        setSelectedProject(res.data.items[0].id)
      }
    } catch (err) {
      message.error('Failed to fetch projects')
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    if (selectedProject) {
      fetchDocuments()
    }
  }, [selectedProject])

  const handleUpload = async (file: File) => {
    if (!selectedProject) {
      message.warning('Please select a project first')
      return false
    }
    try {
      await documentService.uploadDocument(file, selectedProject)
      message.success('Document uploaded')
      fetchDocuments()
    } catch (err) {
      message.error('Failed to upload document')
    }
    return false
  }

  const handleDelete = async (id: string) => {
    try {
      await documentService.deleteDocument(id)
      message.success('Document deleted')
      fetchDocuments()
    } catch (err) {
      message.error('Failed to delete document')
    }
  }

  const columns = [
    { title: 'Title', dataIndex: 'title', key: 'title' },
    { title: 'Format', dataIndex: 'format', key: 'format' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at', render: (t: string) => new Date(t).toLocaleString() },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: Document) => (
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
      <div style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center' }}>
        <Select
          placeholder="Select Project"
          style={{ width: 200 }}
          value={selectedProject}
          onChange={setSelectedProject}
          options={projects.map(p => ({ label: p.name, value: p.id }))}
        />
        <Upload beforeUpload={handleUpload} showUploadList={false}>
          <Button icon={<UploadOutlined />}>Upload Document</Button>
        </Upload>
      </div>

      <Table columns={columns} dataSource={documents} rowKey="id" loading={loading} />
    </div>
  )
}
