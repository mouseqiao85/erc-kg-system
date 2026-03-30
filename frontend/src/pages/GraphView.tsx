import { useState, useEffect, useCallback, useRef } from 'react'
import { Select, Button, Card, Row, Col, Statistic, Spin, Input, Space, Dropdown, message } from 'antd'
import { ReloadOutlined, SearchOutlined, ZoomInOutlined, ExpandOutlined, DownloadOutlined, MenuOutlined } from '@ant-design/icons'
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  NodeTypes,
  Handle,
  Position,
  useReactFlow,
  ReactFlowProvider,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import dagre from 'dagre'
import { graphService, projectService, entityService } from '../services/api'

interface GraphNode {
  id: string
  name: string
  type: string
}

interface GraphEdge {
  id: string
  source: string
  target: string
  relation: string
}

const { Search } = Input

const CustomNode = ({ data }: { data: { label: string; type: string; highlighted?: boolean } }) => {
  return (
    <div style={{ 
      padding: '10px 15px', 
      border: `2px solid ${data.highlighted ? '#faad14' : '#1890ff'}`, 
      borderRadius: 8, 
      background: data.highlighted ? '#fffbe6' : '#e6f7ff',
      minWidth: 100,
      textAlign: 'center'
    }}>
      <Handle type="target" position={Position.Top} />
      <div style={{ fontWeight: 'bold' }}>{data.label}</div>
      <div style={{ fontSize: 12, color: '#666' }}>{data.type}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}

const nodeTypes: NodeTypes = {
  custom: CustomNode,
}

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  dagreGraph.setGraph({ rankdir: direction })

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 150, height: 80 })
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 75,
        y: nodeWithPosition.y - 40,
      },
    }
  })

  return { nodes: layoutedNodes, edges }
}

function GraphViewInner() {
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])
  const [loading, setLoading] = useState(false)
  const [totalNodes, setTotalNodes] = useState(0)
  const [totalEdges, setTotalEdges] = useState(0)
  const [searchText, setSearchText] = useState('')
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set())
  const [layoutType, setLayoutType] = useState<'force' | 'dagre-tb' | 'dagre-lr'>('force')
  
  const { fitView, setCenter, getNode } = useReactFlow()
  const graphRef = useRef<any>(null)

  const fetchProjects = async () => {
    try {
      const res = await projectService.getProjects()
      setProjects(res.data.items || [])
      if (res.data.items?.length > 0 && !selectedProject) {
        setSelectedProject(res.data.items[0].id)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const fetchGraph = useCallback(async () => {
    if (!selectedProject) return
    setLoading(true)
    try {
      const res = await graphService.getGraph(selectedProject, 200)
      const graphNodes: GraphNode[] = res.data.nodes || []
      const graphEdges: GraphEdge[] = res.data.edges || []

      setTotalNodes(graphNodes.length)
      setTotalEdges(graphEdges.length)

      let flowNodes: Node[] = graphNodes.map((node, idx) => ({
        id: node.id,
        type: 'custom',
        position: {
          x: (idx % 5) * 200 + 50,
          y: Math.floor(idx / 5) * 150 + 50,
        },
        data: { label: node.name, type: node.type },
      }))

      let flowEdges: Edge[] = graphEdges.map((edge, idx) => ({
        id: edge.id || `e${idx}`,
        source: edge.source,
        target: edge.target,
        label: edge.relation,
        animated: true,
        style: { stroke: '#1890ff' },
      }))

      if (layoutType === 'dagre-tb' || layoutType === 'dagre-lr') {
        const direction = layoutType === 'dagre-tb' ? 'TB' : 'LR'
        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          flowNodes,
          flowEdges,
          direction
        )
        flowNodes = layoutedNodes
        flowEdges = layoutedEdges
      }

      setNodes(flowNodes)
      setEdges(flowEdges)
      
      setTimeout(() => {
        fitView({ padding: 0.2 })
      }, 100)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }, [selectedProject, layoutType, setNodes, setEdges, fitView])

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    if (selectedProject) {
      fetchGraph()
    }
  }, [selectedProject, fetchGraph])

  const handleSearch = async () => {
    if (!searchText.trim()) return
    
    try {
      const res = await entityService.getEntities({
        project_id: selectedProject,
        keyword: searchText,
        limit: 10
      })
      const matchedEntities = res.data.items || []
      
      if (matchedEntities.length > 0) {
        const matchedIds = new Set(matchedEntities.map((e: any) => e.id))
        
        setHighlightedNodes(matchedIds)
        
        const matchedNode = nodes.find(n => matchedIds.has(n.id))
        if (matchedNode) {
          setCenter(matchedNode.position.x + 75, matchedNode.position.y + 40, { zoom: 1.5 })
        }
        
        message.success(`Found ${matchedEntities.length} matching entities`)
      } else {
        message.warning('No matching entities found')
      }
    } catch (err) {
      message.error('Search failed')
    }
  }

  const handleNodeClick = async (_: any, node: Node) => {
    try {
      const res = await graphService.getSubgraph(node.id, 2)
      const subgraphNodes = res.data.nodes || []
      const subgraphEdges = res.data.edges || []
      
      if (subgraphNodes.length > 0) {
        const existingIds = new Set(nodes.map(n => n.id))
        const newNodes = subgraphNodes
          .filter((n: any) => !existingIds.has(n.id))
          .map((n: any, idx: number) => ({
            id: n.id,
            type: 'custom',
            position: {
              x: node.position.x + 200 + (idx % 3) * 150,
              y: node.position.y + (idx - 1) * 100,
            },
            data: { label: n.name, type: n.type },
          }))
        
        const newEdges = subgraphEdges.map((e: any, idx: number) => ({
          id: `subgraph-e${idx}`,
          source: e.source,
          target: e.target,
          label: e.label,
          style: { stroke: '#52c41a' },
        }))
        
        setNodes([...nodes, ...newNodes])
        setEdges([...edges, ...newEdges])
        
        message.success(`Loaded ${newNodes.length} related nodes`)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleLayoutChange = (newLayout: 'force' | 'dagre-tb' | 'dagre-lr') => {
    setLayoutType(newLayout)
  }

  const handleExportPNG = async () => {
    try {
      const flowContainer = document.querySelector('.react-flow') as HTMLElement
      if (!flowContainer) return
      
      message.info('Exporting as PNG...')
      
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      
      canvas.width = flowContainer.offsetWidth
      canvas.height = flowContainer.offsetHeight
      
      ctx.fillStyle = '#fafafa'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      const dataUrl = flowContainer.toDataURL('image/png')
      const link = document.createElement('a')
      link.download = `knowledge-graph-${Date.now()}.png`
      link.href = dataUrl
      link.click()
      
      message.success('Exported as PNG')
    } catch (err) {
      message.error('Export failed')
    }
  }

  const handleExportJSON = () => {
    const data = {
      nodes: nodes.map(n => ({ id: n.id, label: n.data.label, type: n.data.type })),
      edges: edges.map(e => ({ source: e.source, target: e.target, label: e.label })),
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.download = `knowledge-graph-${Date.now()}.json`
    link.href = url
    link.click()
    URL.revokeObjectURL(url)
    
    message.success('Exported as JSON')
  }

  const layoutMenuItems = [
    { key: 'force', label: 'Force Layout' },
    { key: 'dagre-tb', label: 'Top to Bottom' },
    { key: 'dagre-lr', label: 'Left to Right' },
  ]

  return (
    <div style={{ height: 'calc(100vh - 200px)' }}>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card><Statistic title="Entities" value={totalNodes} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="Relations" value={totalEdges} /></Card>
        </Col>
      </Row>

      <div style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
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
          onSearch={handleSearch}
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
        />
        
        <Button icon={<ReloadOutlined />} onClick={fetchGraph} loading={loading}>
          Refresh
        </Button>
        
        <Dropdown 
          menu={{ 
            items: layoutMenuItems,
            onClick: ({ key }) => handleLayoutChange(key as any)
          }}
          trigger={['click']}
        >
          <Button icon={<MenuOutlined />}>
            Layout: {layoutType === 'force' ? 'Force' : layoutType === 'dagre-tb' ? 'TB' : 'LR'}
          </Button>
        </Dropdown>
        
        <Button icon={<ZoomInOutlined />} onClick={() => fitView({ padding: 0.2 })}>
          Fit View
        </Button>
        
        <Button icon={<DownloadOutlined />} onClick={handleExportPNG}>
          Export PNG
        </Button>
        
        <Button onClick={handleExportJSON}>
          Export JSON
        </Button>
      </div>

      <Card bodyStyle={{ padding: 0 }} style={{ height: 'calc(100% - 120px)' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Spin size="large" />
          </div>
        ) : nodes.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>
            No graph data. Upload documents and build the graph first.
          </div>
        ) : (
          <ReactFlow
            ref={graphRef}
            nodes={nodes.map(n => ({
              ...n,
              data: { ...n.data, highlighted: highlightedNodes.has(n.id) }
            }))}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            nodeTypes={nodeTypes}
            fitView
            style={{ background: '#fafafa' }}
          >
            <Background />
            <Controls />
          </ReactFlow>
        )}
      </Card>
    </div>
  )
}

export default function GraphView() {
  return (
    <ReactFlowProvider>
      <GraphViewInner />
    </ReactFlowProvider>
  )
}
