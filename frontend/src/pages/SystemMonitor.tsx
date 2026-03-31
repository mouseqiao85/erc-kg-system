import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Progress, List, Space, Button } from 'antd'
import { 
  DatabaseOutlined, 
  CloudServerOutlined, 
  ApiOutlined, 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons'
import { projectService, documentService, entityService, graphService, jobService } from '../services/api'

interface SystemStatus {
  name: string
  status: 'online' | 'offline' | 'warning'
  message: string
  latency?: number
}

export default function SystemMonitor() {
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({
    projects: 0,
    documents: 0,
    entities: 0,
    triples: 0,
    jobs: 0
  })
  const [systemStatus, setSystemStatus] = useState<SystemStatus[]>([])
  const [recentJobs, setRecentJobs] = useState<any[]>([])

  const fetchStats = async () => {
    setLoading(true)
    try {
      const [projRes, docRes, entityRes, tripleRes, jobRes] = await Promise.all([
        projectService.getProjects(),
        documentService.getDocuments({ limit: 1 }),
        entityService.getEntities({ limit: 1 }),
        graphService.getGraph(''),
        jobService.getJobs()
      ])
      
      setStats({
        projects: projRes.data.total || projRes.data.items?.length || 0,
        documents: docRes.data.total || 0,
        entities: entityRes.data.items?.length || 0,
        triples: 0,
        jobs: jobRes.data.items?.length || 0
      })
      
      setRecentJobs(jobRes.data.items?.slice(0, 5) || [])
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const checkSystemStatus = async () => {
    const statuses: SystemStatus[] = []
    
    try {
      const start = Date.now()
      await fetch('/api/v1/health')
      const latency = Date.now() - start
      statuses.push({
        name: 'API Server',
        status: 'online',
        message: 'Running',
        latency
      })
    } catch {
      statuses.push({
        name: 'API Server',
        status: 'offline',
        message: 'Not responding'
      })
    }
    
    setSystemStatus(statuses)
  }

  useEffect(() => {
    fetchStats()
    checkSystemStatus()
    const interval = setInterval(checkSystemStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#52c41a'
      case 'offline': return '#ff4d4f'
      case 'warning': return '#faad14'
      default: return '#d9d9d9'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircleOutlined style={{ color: getStatusColor(status) }} />
      case 'offline': return <ExclamationCircleOutlined style={{ color: getStatusColor(status) }} />
      case 'warning': return <ExclamationCircleOutlined style={{ color: getStatusColor(status) }} />
      default: return null
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', render: (id: string) => id?.slice(0, 8) },
    { title: 'Type', dataIndex: 'type', key: 'type' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'completed' ? 'green' : status === 'running' ? 'blue' : 'default'>
          {status}
        </Tag>
      )
    },
    { title: 'Progress', dataIndex: 'progress', key: 'progress', render: (p: number) => <Progress percent={p || 0} size="small" /> },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at', render: (t: string) => t ? new Date(t).toLocaleString() : '-' },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <Card>
            <Statistic title="Projects" value={stats.projects} prefix={<DatabaseOutlined />} />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic title="Documents" value={stats.documents} prefix={<ApiOutlined />} />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic title="Entities" value={stats.entities} prefix={<CloudServerOutlined />} />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic title="Jobs" value={stats.jobs} prefix={<SyncOutlined />} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="System Status">
            <List
              dataSource={systemStatus}
              renderItem={item => (
                <List.Item>
                  <Space>
                    {getStatusIcon(item.status)}
                    <span>{item.name}</span>
                    <Tag color={getStatusColor(item.status)}>{item.status}</Tag>
                    {item.latency && <span style={{ color: '#999' }}>{item.latency}ms</span>}
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={16}>
          <Card title="Recent Jobs">
            <Table 
              columns={columns} 
              dataSource={recentJobs} 
              rowKey="id" 
              loading={loading}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Quick Actions">
            <Space direction="vertical" style={{ width: '100%' }}>
              <a href="/projects"><Button block>Create New Project</Button></a>
              <a href="/documents"><Button block>Upload Documents</Button></a>
              <a href="/jobs"><Button block>Build Knowledge Graph</Button></a>
              <a href="/graph"><Button block>View Graph</Button></a>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
