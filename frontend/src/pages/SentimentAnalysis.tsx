import { useState, useEffect, useRef, useCallback } from 'react'
import { Select, Button, Card, Row, Col, Statistic, Spin, Input, Space, Tabs, Tag, Modal, List, Timeline, message } from 'antd'
import { ReloadOutlined, SearchOutlined, WarningOutlined, LineChartOutlined, ApartmentOutlined, FireOutlined } from '@ant-design/icons'
import * as d3 from 'd3'
import { sentimentService, customerService, eventService } from '../services/api'

const { Search } = Input
const { TabPane } = Tabs

interface GraphNode {
  id: string
  type: string
  name: string
  industry?: string
  sentiment_score: number
  influence_level?: string
  color?: string
}

interface GraphEdge {
  id: string
  source: string
  target: string
  type: string
  weight: number
}

export default function SentimentAnalysis() {
  const [activeTab, setActiveTab] = useState('industry')
  const [viewMode, setViewMode] = useState<'industry' | 'customer' | 'event' | 'cluster'>('industry')
  const [loading, setLoading] = useState(false)
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [detailVisible, setDetailVisible] = useState(false)
  const [alerts, setAlerts] = useState<any[]>([])
  const [industry, setIndustry] = useState<string>('科技')
  const [keyword, setKeyword] = useState('')
  
  const svgRef = useRef<SVGSVGElement>(null)
  const simulationRef = useRef<any>(null)

  const fetchIndustryOverview = async () => {
    setLoading(true)
    try {
      const res = await sentimentService.getIndustryOverview()
      setNodes(res.data.nodes || [])
      setEdges(res.data.edges || [])
    } catch (err) {
      message.error('Failed to load industry overview')
    }
    setLoading(false)
  }

  const fetchCustomerNetwork = async (customerId: string) => {
    setLoading(true)
    try {
      const res = await sentimentService.getCustomerNetwork(customerId, 2)
      setNodes(res.data.nodes || [])
      setEdges(res.data.edges || [])
    } catch (err) {
      message.error('Failed to load customer network')
    }
    setLoading(false)
  }

  const fetchEventEvolution = async (eventId: string) => {
    setLoading(true)
    try {
      const res = await sentimentService.getEventEvolution(eventId, true)
      setNodes(res.data.nodes || [])
      setEdges(res.data.edges || [])
    } catch (err) {
      message.error('Failed to load event evolution')
    }
    setLoading(false)
  }

  const fetchHotspotClusters = async () => {
    setLoading(true)
    try {
      const res = await sentimentService.getHotspotClusters(industry, 20)
      setNodes(res.data.nodes || [])
      setEdges(res.data.edges || [])
    } catch (err) {
      message.error('Failed to load hotspot clusters')
    }
    setLoading(false)
  }

  const fetchAlerts = async () => {
    try {
      const res = await sentimentService.getAlerts('high', 'active')
      setAlerts(res.data.items || [])
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [])

  useEffect(() => {
    if (viewMode === 'industry') {
      fetchIndustryOverview()
    } else if (viewMode === 'cluster') {
      fetchHotspotClusters()
    }
  }, [viewMode, industry])

  const renderGraph = useCallback(() => {
    if (!svgRef.current || nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight

    svg.attr('width', width).attr('height', height)

    const g = svg.append('g')

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom)

    const nodeMap = new Map(nodes.map(n => [n.id, n]))

    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(edges as any).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50))

    simulationRef.current = simulation

    const link = g.append('g')
      .selectAll('line')
      .data(edges)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.max(d.weight * 2, 1))

    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('cursor', 'pointer')
      .on('click', (event, d) => {
        setSelectedNode(d)
        setDetailVisible(true)
      })

    node.append('circle')
      .attr('r', (d: any) => {
        if (d.type === 'Industry') return 30
        if (d.type === 'Event') return 20
        return 15
      })
      .attr('fill', (d: any) => {
        if (d.color) return d.color
        const score = d.sentiment_score || 0.5
        return score > 0.6 ? '#52c41a' : score < 0.4 ? '#ff4d4f' : '#d9d9d9'
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)

    node.append('text')
      .text((d: any) => d.name.length > 15 ? d.name.slice(0, 15) + '...' : d.name)
      .attr('x', 0)
      .attr('y', 35)
      .attr('text-anchor', 'middle')
      .attr('font-size', 10)
      .attr('fill', '#666')

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
    })
  }, [nodes, edges])

  useEffect(() => {
    renderGraph()
    window.addEventListener('resize', renderGraph)
    return () => window.removeEventListener('resize', renderGraph)
  }, [renderGraph])

  const handleNodeClick = async (node: GraphNode) => {
    if (node.type === 'Customer') {
      setViewMode('customer')
      fetchCustomerNetwork(node.id)
    } else if (node.type === 'Event') {
      setViewMode('event')
      fetchEventEvolution(node.id)
    }
  }

  const industries = ['制造', '能源', '金融', '科技']

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="Total Entities" value={nodes.length} prefix={<ApartmentOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Relations" value={edges.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Active Alerts" value={alerts.length} prefix={<WarningOutlined />} valueStyle={{ color: alerts.length > 0 ? '#ff4d4f' : '#52c41a' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Positive Rate" value={nodes.length > 0 ? Math.round((nodes.filter(n => (n.sentiment_score || 0.5) > 0.6).length / nodes.length) * 100) : 0} suffix="%" prefix={<FireOutlined />} />
          </Card>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="Industry Overview" key="industry">
          <Card style={{ marginBottom: 16 }}>
            <Space>
              <Select
                placeholder="Select Industry"
                style={{ width: 150 }}
                value={industry}
                onChange={setIndustry}
                options={industries.map(i => ({ label: i, value: i }))}
              />
              <Button icon={<ReloadOutlined />} onClick={fetchIndustryOverview}>Refresh</Button>
            </Space>
          </Card>
        </TabPane>
        <TabPane tab="Customer Network" key="customer">
          <Card style={{ marginBottom: 16 }}>
            <Space>
              <Search
                placeholder="Search customer..."
                style={{ width: 200 }}
                onSearch={setKeyword}
              />
            </Space>
          </Card>
        </TabPane>
        <TabPane tab="Event Timeline" key="event">
          <Card style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <List
                  size="small"
                  header="Recent Events"
                  dataSource={alerts.slice(0, 5)}
                  renderItem={item => (
                    <List.Item>
                      <Space>
                        <Tag color={item.severity === 'high' ? 'red' : 'orange'}>{item.severity}</Tag>
                        <span>{item.title}</span>
                      </Space>
                    </List.Item>
                  )}
                />
              </Col>
              <Col span={12}>
                <Timeline>
                  {alerts.map((alert, idx) => (
                    <Timeline.Item key={idx} color={alert.severity === 'high' ? 'red' : 'blue'}>
                      <strong>{alert.title}</strong>
                      <p>Severity: {alert.severity}</p>
                    </Timeline.Item>
                  ))}
                </Timeline>
              </Col>
            </Row>
          </Card>
        </TabPane>
        <TabPane tab="Hotspot Clusters" key="cluster">
          <Card style={{ marginBottom: 16 }}>
            <Space>
              <Select
                placeholder="Select Industry"
                style={{ width: 150 }}
                value={industry}
                onChange={setIndustry}
                options={industries.map(i => ({ label: i, value: i }))}
              />
              <Button icon={<ReloadOutlined />} onClick={fetchHotspotClusters}>Refresh</Button>
            </Space>
          </Card>
        </TabPane>
      </Tabs>

      <Card bodyStyle={{ padding: 0 }} style={{ height: 500 }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 500 }}>
            <Spin size="large" />
          </div>
        ) : (
          <svg ref={svgRef} style={{ width: '100%', height: 500 }} />
        )}
      </Card>

      <Modal
        title={`Node Details: ${selectedNode?.name}`}
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={600}
      >
        {selectedNode && (
          <div>
            <Row gutter={16}>
              <Col span={12}>
                <p><strong>Type:</strong> <Tag>{selectedNode.type}</Tag></p>
              </Col>
              <Col span={12}>
                <p><strong>Sentiment Score:</strong> {((selectedNode.sentiment_score || 0.5) * 100).toFixed(1)}%</p>
              </Col>
            </Row>
            {selectedNode.industry && (
              <p><strong>Industry:</strong> {selectedNode.industry}</p>
            )}
            {selectedNode.influence_level && (
              <p><strong>Influence:</strong> <Tag color="blue">{selectedNode.influence_level}</Tag></p>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
