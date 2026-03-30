import { useState, useEffect } from 'react'
import { Table, Button, Space, Input, Select, Tag, Modal, Card, Row, Col, Statistic, message, Popconfirm } from 'antd'
import { DeleteOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import { entityService, tripleService, projectService } from '../services/api'

const { Search } = Input

interface Entity {
  id: string
  name: string
  type: string
  confidence: number
  project_id: string
  created_at: string
}

interface Triple {
  id: string
  head: string
  relation: string
  tail: string
  confidence: number
  valid: boolean
  project_id: string
}

export default function Entities() {
  const [entities, setEntities] = useState<Entity[]>([])
  const [triples, setTriples] = useState<Triple[]>([])
  const [loading, setLoading] = useState(false)
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [keyword, setKeyword] = useState('')
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)
  const [detailVisible, setDetailVisible] = useState(false)

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

  const fetchEntities = async () => {
    if (!selectedProject) return
    setLoading(true)
    try {
      const res = await entityService.getEntities({
        project_id: selectedProject,
        keyword: keyword || undefined,
        limit: 100
      })
      setEntities(res.data.items || [])
    } catch (err) {
      message.error('Failed to fetch entities')
    }
    setLoading(false)
  }

  const fetchTriples = async () => {
    if (!selectedProject) return
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
      setTriples(mapped)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    if (selectedProject) {
      fetchEntities()
      fetchTriples()
    }
  }, [selectedProject, keyword])

  const handleDelete = async (id: string) => {
    try {
      await entityService.deleteEntity(id)
      message.success('Entity deleted')
      fetchEntities()
    } catch (err) {
      message.error('Failed to delete entity')
    }
  }

  const handleViewDetail = (entity: Entity) => {
    setSelectedEntity(entity)
    setDetailVisible(true)
  }

  const entityColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name', fixed: 'left' as const, width: 150 },
    { title: 'Type', dataIndex: 'type', key: 'type', width: 100, render: (type: string) => <Tag color="blue">{type || 'Unknown'}</Tag> },
    { title: 'Confidence', dataIndex: 'confidence', key: 'confidence', width: 100, render: (v: number) => v ? v.toFixed(2) : '-' },
    { 
      title: 'Related Triples', 
      key: 'triples',
      width: 120,
      render: (_: any, record: Entity) => {
        const count = triples.filter(t => t.head === record.name || t.tail === record.name).length
        return <Tag color="green">{count} triples</Tag>
      }
    },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at', width: 180, render: (t: string) => new Date(t).toLocaleString() },
    {
      title: 'Action',
      key: 'action',
      width: 120,
      render: (_: any, record: Entity) => (
        <Space>
          <Button type="link" onClick={() => handleViewDetail(record)}>View</Button>
          <Popconfirm title="Delete this entity?" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />}>Delete</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const entityTriples = selectedEntity 
    ? triples.filter(t => t.head === selectedEntity.name || t.tail === selectedEntity.name)
    : []

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card><Statistic title="Entities" value={entities.length} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="Triples" value={triples.length} /></Card>
        </Col>
      </Row>

      <Card title="Entities Management" style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="Select Project"
            style={{ width: 200 }}
            value={selectedProject}
            onChange={setSelectedProject}
            options={projects.map(p => ({ label: p.name, value: p.id }))}
          />
          <Search
            placeholder="Search entities..."
            allowClear
            style={{ width: 200 }}
            onSearch={setKeyword}
            prefix={<SearchOutlined />}
          />
          <Button icon={<ReloadOutlined />} onClick={fetchEntities}>Refresh</Button>
        </Space>

        <Table 
          columns={entityColumns} 
          dataSource={entities} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 20 }}
          scroll={{ x: 800 }}
          size="small"
        />
      </Card>

      <Modal
        title={`Entity Details: ${selectedEntity?.name}`}
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={700}
      >
        {selectedEntity && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <strong>Type:</strong> {selectedEntity.type || 'Unknown'}
              </Col>
              <Col span={12}>
                <strong>Confidence:</strong> {selectedEntity.confidence?.toFixed(2) || '-'}
              </Col>
            </Row>
            <h4>Related Triples ({entityTriples.length})</h4>
            <Table
              dataSource={entityTriples}
              rowKey="id"
              size="small"
              pagination={false}
              columns={[
                { title: 'Head', dataIndex: 'head', key: 'head' },
                { title: 'Relation', dataIndex: 'relation', key: 'relation', render: (r: string) => <Tag>{r}</Tag> },
                { title: 'Tail', dataIndex: 'tail', key: 'tail' },
              ]}
            />
          </div>
        )}
      </Modal>
    </div>
  )
}
