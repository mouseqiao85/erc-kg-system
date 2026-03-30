import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Row, Col, Statistic, Select, Progress, Tag, message, Modal } from 'antd'
import { PlayCircleOutlined, WifiOutlined } from '@ant-design/icons'
import { jobService, projectService, documentService } from '../services/api'
import { useWebSocket } from '../services/websocket'

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
  const [selectedJob, setSelectedJob] = useState<string | null>(null)
  const [wsModalVisible, setWsModalVisible] = useState(false)

  const { progress, status: wsStatus, currentStep, isConnected, result: wsResult } = useWebSocket(selectedJob)

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

  useEffect(() => {
    if (wsStatus === 'completed') {
      message.success('Job completed successfully!')
      fetchJobs()
      setWsModalVisible(false)
      setSelectedJob(null)
    } else if (wsStatus === 'failed') {
      message.error('Job failed!')
      fetchJobs()
    }
  }, [wsStatus])

  const handleBuild = async () => {
    if (!selectedProject || selectedDocs.length === 0) {
      message.warning('Please select project and documents')
      return
    }
    try {
      const res = await jobService.createJob({
        project_id: selectedProject,
        doc_ids: selectedDocs,
        config: {
          entity_types: [],
          llm_model: 'gpt-4',
          temperature: 0.7,
          enable_validation: true
        }
      })
      const jobId = res.data.job_id
      message.success('Job started!')
      setSelectedJob(jobId)
      setWsModalVisible(true)
      fetchJobs()
    } catch (err) {
      message.error('Failed to start job')
    }
  }

  const handleViewProgress = (jobId: string) => {
    setSelectedJob(jobId)
    setWsModalVisible(true)
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', render: (id: string) => id?.slice(0, 8) },
    { title: 'Type', dataIndex: 'type', key: 'type' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => {
        const color = status === 'completed' ? 'green' : status === 'running' ? 'blue' : status === 'failed' ? 'red' : 'default'
        return <Tag color={color}>{status}</Tag>
      }
    },
    { title: 'Progress', dataIndex: 'progress', key: 'progress', render: (p: number) => <Progress percent={p || 0} size="small" /> },
    { title: 'Step', dataIndex: 'current_step', key: 'current_step' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at', render: (t: string) => new Date(t).toLocaleString() },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: Job) => (
        record.status === 'running' ? (
          <Button type="link" onClick={() => handleViewProgress(record.id)}>
            View Progress
          </Button>
        ) : null
      ),
    },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card><Statistic title="Total Jobs" value={jobs.length} /></Card>
        </Col>
      </Row>

      <Card title="Build Knowledge Graph" style={{ marginBottom: 16 }}>
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

      <Modal
        title={
          <Space>
            <WifiOutlined style={{ color: isConnected ? '#52c41a' : '#ff4d4f' }} />
            Job Progress
          </Space>
        }
        open={wsModalVisible}
        onCancel={() => {
          setWsModalVisible(false)
          setSelectedJob(null)
        }}
        footer={[
          <Button key="close" onClick={() => {
            setWsModalVisible(false)
            setSelectedJob(null)
          }}>
            Close
          </Button>
        ]}
        width={500}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Statistic 
              title="Status" 
              value={wsStatus || 'pending'} 
              valueStyle={{ color: wsStatus === 'completed' ? '#52c41a' : wsStatus === 'failed' ? '#ff4d4f' : '#1890ff' }}
            />
          </div>
          
          <div>
            <div style={{ marginBottom: 8 }}>Progress</div>
            <Progress 
              percent={progress} 
              status={wsStatus === 'completed' ? 'success' : wsStatus === 'failed' ? 'exception' : 'active'}
            />
          </div>

          <div>
            <div style={{ marginBottom: 8 }}>Current Step</div>
            <Tag color="blue">{currentStep || 'Waiting...'}</Tag>
          </div>

          {wsResult && (
            <div>
              <div style={{ marginBottom: 8 }}>Result</div>
              <Card size="small">
                <pre style={{ margin: 0, fontSize: 12 }}>
                  {JSON.stringify(wsResult, null, 2)}
                </pre>
              </Card>
            </div>
          )}
        </Space>
      </Modal>
    </div>
  )
}
