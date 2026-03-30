import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Table } from 'antd'
import { ProjectOutlined, FileTextOutlined, ApartmentOutlined, SyncOutlined } from '@ant-design/icons'
import { projectService, documentService, jobService, graphService } from '../services/api'

interface Stats {
  projects: number
  documents: number
  entities: number
  jobs: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    projects: 0,
    documents: 0,
    entities: 0,
    jobs: 0
  })
  const [recentJobs, setRecentJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const fetchStats = async () => {
    setLoading(true)
    try {
      const [projRes, docRes, jobRes] = await Promise.all([
        projectService.getProjects(),
        documentService.getDocuments(),
        jobService.getJobs()
      ])
      
      const projects = projRes.data.items?.length || 0
      const documents = docRes.data.items?.length || 0
      const jobs = jobRes.data.items?.length || 0
      
      let entities = 0
      if (projects > 0) {
        const firstProject = projRes.data.items[0].id
        try {
          const graphRes = await graphService.getGraph(firstProject, 100)
          entities = graphRes.data.nodes?.length || 0
        } catch {}
      }
      
      setStats({ projects, documents, entities, jobs })
      
      const jobsList = jobRes.data.items || []
      setRecentJobs(jobsList.slice(0, 5))
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchStats()
  }, [])

  const jobColumns = [
    { title: 'ID', dataIndex: 'id', key: 'id', render: (id: string) => id?.slice(0, 8) },
    { title: 'Status', dataIndex: 'status', key: 'status' },
    { title: 'Progress', dataIndex: 'progress', key: 'progress', render: (p: number) => `${p || 0}%` },
    { title: 'Step', dataIndex: 'current_step', key: 'current_step' },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="Projects" value={stats.projects} prefix={<ProjectOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Documents" value={stats.documents} prefix={<FileTextOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Entities" value={stats.entities} prefix={<ApartmentOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Jobs" value={stats.jobs} prefix={<SyncOutlined />} /></Card>
        </Col>
      </Row>

      <Card title="Recent Jobs">
        <Table 
          columns={jobColumns} 
          dataSource={recentJobs} 
          rowKey="id" 
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  )
}
