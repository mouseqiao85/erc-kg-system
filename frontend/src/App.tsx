import { Routes, Route } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  ProjectOutlined,
  FileTextOutlined,
  ApartmentOutlined,
  DashboardOutlined,
  SearchOutlined,
  TeamOutlined,
  LinkOutlined,
  SettingOutlined,
  LineChartOutlined,
  BarChartOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import DashboardStats from './pages/DashboardStats'
import Projects from './pages/Projects'
import Documents from './pages/Documents'
import GraphView from './pages/GraphView'
import Jobs from './pages/Jobs'
import Query from './pages/Query'
import Entities from './pages/Entities'
import Triples from './pages/Triples'
import Settings from './pages/Settings'
import SentimentAnalysis from './pages/SentimentAnalysis'
import './App.css'

const { Header, Sider, Content } = Layout

function App() {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/stats', icon: <BarChartOutlined />, label: 'Statistics' },
    { key: '/projects', icon: <ProjectOutlined />, label: 'Projects' },
    { key: '/documents', icon: <FileTextOutlined />, label: 'Documents' },
    { key: '/graph', icon: <ApartmentOutlined />, label: 'Knowledge Graph' },
    { key: '/query', icon: <SearchOutlined />, label: 'Query' },
    { key: '/sentiment', icon: <LineChartOutlined />, label: 'Sentiment Analysis' },
    { key: '/entities', icon: <TeamOutlined />, label: 'Entities' },
    { key: '/triples', icon: <LinkOutlined />, label: 'Triples' },
    { key: '/jobs', icon: <SettingOutlined />, label: 'Jobs' },
    { key: '/settings', icon: <SettingOutlined />, label: 'Settings' },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" width={220}>
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid #f0f0f0' }}>
          <h2 style={{ margin: 0, color: '#1890ff' }}>ERC-KG</h2>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
          <div style={{ float: 'right', display: 'flex', alignItems: 'center', gap: 16 }}>
            <span>Admin</span>
          </div>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: '#fff', minHeight: 280, borderRadius: 8 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stats" element={<DashboardStats />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/graph" element={<GraphView />} />
            <Route path="/query" element={<Query />} />
            <Route path="/sentiment" element={<SentimentAnalysis />} />
            <Route path="/entities" element={<Entities />} />
            <Route path="/triples" element={<Triples />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default App
