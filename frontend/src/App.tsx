import { Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout, ProtectedRoute } from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
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
import SystemMonitor from './pages/SystemMonitor'
import SentimentTasks from './pages/SentimentTasks'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/stats" element={<DashboardStats />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/documents" element={<Documents />} />
                <Route path="/graph" element={<GraphView />} />
                <Route path="/query" element={<Query />} />
                <Route path="/sentiment" element={<SentimentAnalysis />} />
                <Route path="/sentiment-tasks" element={<SentimentTasks />} />
                <Route path="/entities" element={<Entities />} />
                <Route path="/triples" element={<Triples />} />
                <Route path="/jobs" element={<Jobs />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/monitor" element={<SystemMonitor />} />
              </Routes>
            </MainLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
