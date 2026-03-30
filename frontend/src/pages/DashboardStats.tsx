import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Select, DatePicker, Space, Button, List, Tag, Timeline, Progress, message } from 'antd'
import { LineChartOutlined, PieChartOutlined, BarChartOutlined, WarningOutlined, ReloadOutlined } from '@ant-design/icons'
import { Line, Pie, Column } from '@ant-design/charts'
import { sentimentService, eventService, customerService, articleService } from '../services/api'

const { RangePicker } = DatePicker

interface TrendData {
  date: string
  score: number
  count: number
}

interface IndustryData {
  industry: string
  count: number
  positive: number
  negative: number
}

interface AlertData {
  id: string
  title: string
  type: string
  severity: string
  status: string
}

export default function DashboardStats() {
  const [loading, setLoading] = useState(false)
  const [industry, setIndustry] = useState('科技')
  const [trendData, setTrendData] = useState<TrendData[]>([])
  const [industryStats, setIndustryStats] = useState<IndustryData[]>([])
  const [alerts, setAlerts] = useState<AlertData[]>([])
  const [customerStats, setCustomerStats] = useState({ total: 0, positive: 0, negative: 0, neutral: 0 })
  const [articleStats, setArticleStats] = useState({ total: 0, today: 0, positive: 0, negative: 0 })

  const fetchTrendData = async () => {
    setLoading(true)
    try {
      const res = await sentimentService.getIndustryTrend(industry, 'week')
      setTrendData(res.data.trend || [])
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const fetchIndustryStats = async () => {
    try {
      const res = await sentimentService.getIndustryOverview()
      const stats = res.data.statistics?.industry_distribution || {}
      const formatted: IndustryData[] = Object.entries(stats).map(([industry, data]: [string, any]) => ({
        industry,
        count: data.count,
        positive: data.positive,
        negative: data.negative
      }))
      setIndustryStats(formatted)
    } catch (err) {
      console.error(err)
    }
  }

  const fetchAlerts = async () => {
    try {
      const res = await sentimentService.getAlerts('high', 'active')
      setAlerts(res.data.items || [])
    } catch (err) {
      console.error(err)
    }
  }

  const fetchCustomerStats = async () => {
    try {
      const res = await customerService.getCustomers({ limit: 100 })
      const customers = res.data.items || []
      const positive = customers.filter((c: any) => (c.sentiment_score || 0.5) > 0.6).length
      const negative = customers.filter((c: any) => (c.sentiment_score || 0.5) < 0.4).length
      const neutral = customers.length - positive - negative
      setCustomerStats({
        total: customers.length,
        positive,
        negative,
        neutral
      })
    } catch (err) {
      console.error(err)
    }
  }

  const fetchArticleStats = async () => {
    try {
      const res = await articleService.getArticles({ limit: 100 })
      const articles = res.data.items || []
      const today = new Date().toDateString()
      const todayCount = articles.filter((a: any) => new Date(a.publish_time).toDateString() === today).length
      const positive = articles.filter((a: any) => (a.sentiment_score?.overall || 0.5) > 0.6).length
      const negative = articles.filter((a: any) => (a.sentiment_score?.overall || 0.5) < 0.4).length
      setArticleStats({
        total: articles.length,
        today: todayCount,
        positive,
        negative
      })
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchTrendData()
    fetchIndustryStats()
    fetchAlerts()
    fetchCustomerStats()
    fetchArticleStats()
  }, [industry])

  const lineData = trendData.map(d => ({
    date: d.date,
    value: d.score * 100,
    category: 'Sentiment'
  }))

  const lineConfig = {
    data: lineData,
    xField: 'date',
    yField: 'value',
    smooth: true,
    color: '#1890ff',
    point: { size: 3, shape: 'circle' },
    yAxis: {
      min: 0,
      max: 100,
      label: { formatter: (v: number) => `${v}%` }
    },
    tooltip: { showMarkers: false }
  }

  const pieData = [
    { type: 'Positive', value: customerStats.positive },
    { type: 'Neutral', value: customerStats.neutral },
    { type: 'Negative', value: customerStats.negative },
  ].filter(d => d.value > 0)

  const pieConfig = {
    data: pieData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: { type: 'outer', content: '{name}: {value}' },
    color: ['#52c41a', '#d9d9d9', '#ff4d4f']
  }

  const columnData = industryStats.map(d => ({
    industry: d.industry,
    positive: d.positive,
    negative: d.negative
  }))

  const columnConfig = {
    data: columnData.slice(0, 4),
    xField: 'industry',
    yField: 'positive',
    color: '#52c41a',
    label: { position: 'top' as const }
  }

  const industries = ['制造', '能源', '金融', '科技']

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="Total Customers" value={customerStats.total} prefix={<LineChartOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Total Articles" value={articleStats.total} prefix={<BarChartOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Today's Articles" value={articleStats.today} prefix={<PieChartOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Active Alerts" 
              value={alerts.length} 
              prefix={<WarningOutlined />} 
              valueStyle={{ color: alerts.length > 0 ? '#ff4d4f' : '#52c41a' }} 
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card 
            title="Sentiment Trend" 
            extra={
              <Space>
                <Select
                  value={industry}
                  onChange={setIndustry}
                  style={{ width: 100 }}
                  options={industries.map(i => ({ label: i, value: i }))}
                />
                <Button icon={<ReloadOutlined />} onClick={fetchTrendData}>Refresh</Button>
              </Space>
            }
          >
            {trendData.length > 0 ? <Line {...lineConfig} height={250} /> : <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>No data</div>}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Customer Sentiment Distribution">
            {pieData.length > 0 ? <Pie {...pieConfig} height={250} /> : <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>No data</div>}
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="Industry Statistics">
            {columnData.length > 0 ? <Column {...columnConfig} height={250} /> : <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>No data</div>}
          </Card>
        </Col>
        <Col span={12}>
          <Card 
            title="Recent Alerts" 
            extra={<Tag color="red">{alerts.length} Active</Tag>}
          >
            <List
              size="small"
              dataSource={alerts.slice(0, 5)}
              renderItem={item => (
                <List.Item>
                  <Space>
                    <Tag color={item.severity === 'critical' ? 'red' : item.severity === 'high' ? 'orange' : 'blue'}>
                      {item.severity}
                    </Tag>
                    <span>{item.title}</span>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Card title="Article Sentiment">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <span>Positive: </span>
                <Progress percent={articleStats.total > 0 ? Math.round(articleStats.positive / articleStats.total * 100) : 0} status="success" size="small" />
              </div>
              <div>
                <span>Negative: </span>
                <Progress percent={articleStats.total > 0 ? Math.round(articleStats.negative / articleStats.total * 100) : 0} status="exception" size="small" />
              </div>
            </Space>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Customer Status">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Tag color="green">Positive: {customerStats.positive}</Tag>
                <Tag color="default">Neutral: {customerStats.neutral}</Tag>
                <Tag color="red">Negative: {customerStats.negative}</Tag>
              </div>
            </Space>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Quick Stats">
            <Statistic title="Positive Rate" value={customerStats.total > 0 ? Math.round(customerStats.positive / customerStats.total * 100) : 0} suffix="%" />
            <Statistic title="Negative Rate" value={customerStats.total > 0 ? Math.round(customerStats.negative / customerStats.total * 100) : 0} suffix="%" />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
