import { useState, useEffect } from 'react'
import { Select, Button, Space, Input, Card, Row, Col, Statistic } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { graphService, projectService } from '../services/api'

interface GraphNode {
  id: string
  label: string
  type: string
}

interface GraphEdge {
  source: string
  target: string
  label: string
}

export default function GraphView() {
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])
  const [loading, setLoading] = useState(false)

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

  const fetchGraph = async () => {
    if (!selectedProject) return
    setLoading(true)
    try {
      const res = await graphService.getGraph(selectedProject)
      setNodes(res.data.nodes || [])
      setEdges(res.data.edges || [])
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    if (selectedProject) {
      fetchGraph()
    }
  }, [selectedProject])

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card><Statistic title="Entities" value={nodes.length} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="Relations" value={edges.length} /></Card>
        </Col>
      </Row>

      <div style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center' }}>
        <Select
          placeholder="Select Project"
          style={{ width: 200 }}
          value={selectedProject}
          onChange={setSelectedProject}
          options={projects.map(p => ({ label: p.name, value: p.id }))}
        />
        <Button icon={<ReloadOutlined />} onClick={fetchGraph} loading={loading}>
          Refresh
        </Button>
      </div>

      <Card title="Knowledge Graph" style={{ minHeight: 400 }}>
        <div style={{ padding: 20, textAlign: 'center', color: '#999' }}>
          {nodes.length === 0 ? 'No graph data. Upload documents and build the graph first.' : `Loaded ${nodes.length} nodes and ${edges.length} edges`}
        </div>
      </Card>
    </div>
  )
}
