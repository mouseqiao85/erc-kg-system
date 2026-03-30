import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Row, Col, Statistic, Select, Progress, Tag } from 'antd'
import { PlayCircleOutlined } from '@ant-design/icons'
import { jobService, projectService, documentService } from '../services/api'

interface Job {
  id: string
  type: string
  status: string
  progress: number
  current_step: string
  created_at: string
}

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(false)
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([])
  const [documents, setDocuments] = useState<{ id: string; title: string }[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [selectedDocs, setSelectedDocs] = useState<string[]>([])

  const fetchJobs = async () => {
    if (!selectedProject) return
    setLoading(true)
    try {
      const res = await jobService.getJobs(selectedProject)
      setJobs(res.data.items || [])
    } catch (err) {
      console.error(err)
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
      console.error(err)
    }
  }

  const fetchDocuments = async () => {
    if (!selectedProject) return
    try {
      const res = await documentService.getDocuments({ project_id: selectedProject })
      setDocuments(res.data.items || [])
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    if (selectedProject) {
      fetchJobs()
      fetchDocuments()
    }
  }, [selectedProject])

  const handleBuild = async () => {
    if (!selectedProject || selectedDocs.length === 0) {
      console.error('Please select project and documents')
      return
    }
    try {
      await jobService.createJob({
        project_id: selectedProject,
        doc_ids: selectedDocs,
        config: {
          entity_types: [],
          llm_model: 'gpt-4',
          temperature: 0.7,
          enable_validation: true
        }
      })
      fetchJobs()
    } catch (err) {
      console.error(err)
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', render: (id: string) => id.slice(0, 8) },
    { title: 'Type', dataIndex: 'type', key: 'type' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => {
        const color = status === 'completed' ? 'green' : status === 'running' ? 'blue' : 'default'
        return <Tag color={color}>{status}</Tag>
      }
    },
    { title: 'Progress', dataIndex: 'progress', key: 'progress', render: (p: number) => <Progress percent={p} size="small" /> },
    { title: 'Step', dataIndex: 'current_step', key: 'current_step' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at', render: (t: string) => new Date(t).toLocaleString() },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card><Statistic title="Total Jobs" value={jobs.length} /></Card>
        </Col>
      </Row>

      <Card title="Build Knowledge Graph" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Select
            placeholder="Select Project"
            style={{ width: 200 }}
            value={selectedProject}
            onChange={setSelectedProject}
            options={projects.map(p => ({ label: p.name, value: p.id }))}
          />
          <Select
            mode="multiple"
            placeholder="Select Documents"
            style={{ width: '100%' }}
            value={selectedDocs}
            onChange={setSelectedDocs}
            options={documents.map(d => ({ label: d.title, value: d.id }))}
          />
          <Button type="primary" icon={<PlayCircleOutlined />} onClick={handleBuild} disabled={!selectedProject || selectedDocs.length === 0}>
            Start Building
          </Button>
        </Space>
      </Card>

      <Table columns={columns} dataSource={jobs} rowKey="id" loading={loading} />
    </div>
  )
}
