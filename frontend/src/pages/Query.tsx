import { useState } from 'react'
import { Card, Tabs, Input, Button, Select, Table, Tag, message, Spin, Space, Typography } from 'antd'
import { SearchOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { graphService, projectService } from '../services/api'

const { TextArea } = Input
const { Text } = Typography

export default function QueryPage() {
  const [activeTab, setActiveTab] = useState('natural')
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any>(null)
  const [cypherResults, setCypherResults] = useState<any[]>([])

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

  const handleNaturalQuery = async () => {
    if (!query.trim()) {
      message.warning('Please enter a question')
      return
    }
    setLoading(true)
    try {
      const res = await graphService.naturalQuery(query, selectedProject)
      setResults(res.data)
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Query failed')
    }
    setLoading(false)
  }

  const handleCypherQuery = async () => {
    if (!query.trim()) {
      message.warning('Please enter a Cypher query')
      return
    }
    setLoading(true)
    try {
      const res = await graphService.queryCypher(query)
      const data = res.data.results || []
      if (data.length > 0) {
        const keys = Object.keys(data[0])
        const formatted = data.map((row: any, idx: number) => ({
          key: idx,
          ...row
        }))
        setCypherResults(formatted)
        const columns = keys.map(key => ({
          title: key,
          dataIndex: key,
          key: key,
          render: (val: any) => {
            if (typeof val === 'object') {
              return <pre style={{ margin: 0, fontSize: 12 }}>{JSON.stringify(val, null, 2)}</pre>
            }
            return String(val ?? '-')
          }
        }))
        setResults({ columns })
      } else {
        setCypherResults([])
        setResults({ columns: [] })
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Query failed')
    }
    setLoading(false)
  }

  const handleQuery = () => {
    if (activeTab === 'natural') {
      handleNaturalQuery()
    } else {
      handleCypherQuery()
    }
  }

  const columns = results?.columns || []

  return (
    <div>
      <Card title="Query Knowledge Graph" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Space>
            <Select
              placeholder="Select Project"
              style={{ width: 200 }}
              value={selectedProject}
              onChange={setSelectedProject}
              options={projects.map(p => ({ label: p.name, value: p.id }))}
            />
          </Space>
          
          <TextArea
            rows={4}
            placeholder={activeTab === 'natural' 
              ? "Ask a question in natural language, e.g., 'What is RSA?'" 
              : "Enter Cypher query, e.g., 'MATCH (n) RETURN n LIMIT 10'"}
            value={query}
            onChange={e => setQuery(e.target.value)}
            style={{ fontFamily: activeTab === 'cypher' ? 'monospace' : 'inherit' }}
          />
          
          <Button 
            type="primary" 
            icon={<PlayCircleOutlined />} 
            onClick={handleQuery}
            loading={loading}
          >
            Execute Query
          </Button>
        </Space>
      </Card>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
        </div>
      ) : results ? (
        <Card title={activeTab === 'natural' ? 'Answer' : 'Query Results'}>
          {activeTab === 'natural' ? (
            <div>
              <Text strong style={{ fontSize: 16 }}>{results.answer}</Text>
              {results.triples?.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <Text strong>Related Triples:</Text>
                  <div style={{ marginTop: 8 }}>
                    {results.triples.map((t: any, idx: number) => (
                      <Tag key={idx} color="blue" style={{ marginBottom: 4 }}>
                        {t.head} - {t.relation} - {t.tail}
                      </Tag>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Table
              dataSource={cypherResults}
              columns={columns}
              pagination={{ pageSize: 10 }}
              scroll={{ x: true }}
            />
          )}
        </Card>
      ) : null}
    </div>
  )
}
