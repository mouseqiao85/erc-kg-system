import { useState, useEffect } from 'react'
import { Table, Button, Space, Select, Tag, Card, Row, Col, Statistic, message, Popconfirm } from 'antd'
import { DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import { tripleService, projectService } from '../services/api'

interface Triple {
  id: string
  head: string
  relation: string
  tail: string
  confidence: number
  valid: boolean
  project_id: string
  created_at: string
}

export default function Triples() {
  const [triples, setTriples] = useState<Triple[]>([])
  const [loading, setLoading] = useState(false)
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [relationFilter, setRelationFilter] = useState<string>('')

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

  const fetchTriples = async () => {
    if (!selectedProject) return
    setLoading(true)
    try {
      const res = await tripleService.getTriples({
        project_id: selectedProject,
        limit: 200
      })
      const items = res.data.items || []
      const mapped = items.map((t: any) => ({
        ...t,
        head: t.head?.name || t.head,
        tail: t.tail?.name || t.tail
      }))
      
      if (relationFilter) {
        const filtered = mapped.filter((t: Triple) => t.relation === relationFilter)
        setTriples(filtered)
      } else {
        setTriples(mapped)
      }
    } catch (err) {
      message.error('Failed to fetch triples')
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    if (selectedProject) {
      fetchTriples()
    }
  }, [selectedProject, relationFilter])

  const handleDelete = async (id: string) => {
    try {
      await tripleService.deleteTriple(id)
      message.success('Triple deleted')
      fetchTriples()
    } catch (err) {
      message.error('Failed to delete triple')
    }
  }

  const relations = [...new Set(triples.map(t => t.relation))]

  const columns = [
    { 
      title: 'Head', 
      dataIndex: 'head', 
      key: 'head', 
      width: 150,
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    { 
      title: 'Relation', 
      dataIndex: 'relation', 
      key: 'relation',
      width: 150,
      render: (text: string) => <Tag color="purple">{text}</Tag>
    },
    { 
      title: 'Tail', 
      dataIndex: 'tail', 
      key: 'tail',
      width: 150,
      render: (text: string) => <Tag color="green">{text}</Tag>
    },
    { title: 'Confidence', dataIndex: 'confidence', key: 'confidence', width: 100, render: (v: number) => v?.toFixed(2) || '-' },
    { 
      title: 'Valid', 
      dataIndex: 'valid', 
      key: 'valid',
      width: 80,
      render: (v: boolean) => <Tag color={v ? 'success' : 'error'}>{v ? 'Valid' : 'Invalid'}</Tag>
    },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at', width: 180, render: (t: string) => new Date(t).toLocaleString() },
    {
      title: 'Action',
      key: 'action',
      width: 100,
      render: (_: any, record: Triple) => (
        <Popconfirm title="Delete this triple?" onConfirm={() => handleDelete(record.id)}>
          <Button type="link" danger icon={<DeleteOutlined />}>Delete</Button>
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card><Statistic title="Total Triples" value={triples.length} /></Card>
        </Col>
        <Col span={12}>
          <Card><Statistic title="Unique Relations" value={relations.length} /></Card>
        </Col>
      </Row>

      <Card title="Triples Management">
        <Space style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="Select Project"
            style={{ width: 200 }}
            value={selectedProject}
            onChange={setSelectedProject}
            options={projects.map(p => ({ label: p.name, value: p.id }))}
          />
          <Select
            placeholder="Filter by relation"
            style={{ width: 200 }}
            allowClear
            value={relationFilter || undefined}
            onChange={setRelationFilter}
            options={relations.map(r => ({ label: r, value: r }))}
          />
          <Button icon={<ReloadOutlined />} onClick={fetchTriples}>Refresh</Button>
        </Space>

        <Table 
          columns={columns} 
          dataSource={triples} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 20 }}
          scroll={{ x: 900 }}
          size="small"
        />
      </Card>
    </div>
  )
}
