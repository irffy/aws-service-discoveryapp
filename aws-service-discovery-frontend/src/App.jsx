import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Loader2, RefreshCw, Cloud, Server, Database, Zap, HardDrive, Network, AlertCircle, CheckCircle } from 'lucide-react'
import './App.css'

// Import service icons
import ec2Icon from './assets/ec2-icon.png'
import s3Icon from './assets/s3-icon.png'
import lambdaIcon from './assets/lambda-icon.png'
import rdsIcon from './assets/rds-icon.png'
import vpcIcon from './assets/vpc-icon.png'
import elbIcon from './assets/elb-icon.png'
import cloudformationIcon from './assets/cloudformation-icon.png'
import ecsIcon from './assets/ecs-icon.png'
import snsIcon from './assets/sns-icon.png'
import sqsIcon from './assets/sqs-icon.png'
import dynamodbIcon from './assets/dynamodb-icon.png'

const API_BASE_URL = 'http://localhost:5000/api'

// Service icon mapping
const serviceIcons = {
  'EC2': ec2Icon,
  'S3': s3Icon,
  'Lambda': lambdaIcon,
  'RDS': rdsIcon,
  'VPC': vpcIcon,
  'ELB': elbIcon,
  'CloudFormation': cloudformationIcon,
  'ECS': ecsIcon,
  'SNS': snsIcon,
  'SQS': sqsIcon,
  'DynamoDB': dynamodbIcon
}

// Service color mapping for enhanced UI
const serviceColors = {
  'EC2': 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900 dark:text-orange-300',
  'S3': 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900 dark:text-green-300',
  'Lambda': 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900 dark:text-amber-300',
  'RDS': 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900 dark:text-blue-300',
  'VPC': 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900 dark:text-purple-300',
  'ELB': 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900 dark:text-red-300',
  'CloudFormation': 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900 dark:text-orange-300',
  'ECS': 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900 dark:text-orange-300',
  'SNS': 'bg-pink-100 text-pink-800 border-pink-200 dark:bg-pink-900 dark:text-pink-300',
  'SQS': 'bg-pink-100 text-pink-800 border-pink-200 dark:bg-pink-900 dark:text-pink-300',
  'DynamoDB': 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900 dark:text-blue-300'
}

function App() {
  const [services, setServices] = useState([])
  const [regions, setRegions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRegion, setSelectedRegion] = useState('all')
  const [selectedService, setSelectedService] = useState('all')
  const [summary, setSummary] = useState({})
  const [lastUpdated, setLastUpdated] = useState(null)

  const getServiceIcon = (serviceType) => {
    return serviceIcons[serviceType] || null
  }

  const getStatusColor = (state) => {
    const lowerState = state?.toLowerCase()
    if (lowerState === 'running' || lowerState === 'active' || lowerState === 'available') {
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
    } else if (lowerState === 'stopped' || lowerState === 'inactive' || lowerState === 'terminated') {
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    } else if (lowerState === 'pending' || lowerState === 'starting') {
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
    }
    return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
  }

  const fetchRegions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/regions`)
      if (!response.ok) throw new Error('Failed to fetch regions')
      const data = await response.json()
      setRegions(data.regions || [])
    } catch (err) {
      console.error('Error fetching regions:', err)
    }
  }

  const fetchServices = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/services`)
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to fetch services')
      }
      const data = await response.json()
      setServices(data.resources || [])
      setSummary(data.service_summary || {})
      setLastUpdated(new Date().toLocaleString())
    } catch (err) {
      setError(err.message)
      console.error('Error fetching services:', err)
    } finally {
      setLoading(false)
    }
  }

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      if (!response.ok) throw new Error('Backend not available')
      return true
    } catch (err) {
      setError('Backend service is not available. Please ensure the Flask server is running.')
      return false
    }
  }

  useEffect(() => {
    const initializeApp = async () => {
      const isHealthy = await checkHealth()
      if (isHealthy) {
        await fetchRegions()
        await fetchServices()
      }
    }
    initializeApp()
  }, [])

  const filteredServices = services.filter(service => {
    const matchesSearch = service.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         service.resource_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         service.service_type?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRegion = selectedRegion === 'all' || service.region === selectedRegion
    const matchesService = selectedService === 'all' || service.service_type === selectedService
    return matchesSearch && matchesRegion && matchesService
  })

  const uniqueServiceTypes = [...new Set(services.map(s => s.service_type))].sort()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              AWS Service Discovery
            </h1>
            <p className="text-muted-foreground text-lg">
              Discover and manage your AWS resources across all regions
            </p>
          </div>
          <div className="flex items-center gap-2">
            {lastUpdated && (
              <span className="text-sm text-muted-foreground">
                Last updated: {lastUpdated}
              </span>
            )}
            <Button onClick={fetchServices} disabled={loading} className="bg-green-600 hover:bg-green-700 text-white">
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Summary Cards */}
        {Object.keys(summary).length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {Object.entries(summary).map(([serviceType, count]) => (
              <Card key={serviceType} className="hover:shadow-lg transition-all duration-200 border-2">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="flex items-center gap-3">
                    {getServiceIcon(serviceType) && (
                      <img 
                        src={getServiceIcon(serviceType)} 
                        alt={`${serviceType} icon`} 
                        className="w-8 h-8"
                      />
                    )}
                    <CardTitle className="text-sm font-medium">{serviceType}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white">{count}</div>
                  <p className="text-xs text-muted-foreground">
                    {count === 1 ? 'resource' : 'resources'}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Filters */}
        <Card className="border-2">
          <CardHeader>
            <CardTitle className="text-xl">Filters</CardTitle>
            <CardDescription>Filter your AWS resources by region, service type, or search term</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block text-blue-700 dark:text-blue-300">Search</label>
                <Input
                  placeholder="Search by name or ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="border-2 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block text-purple-700 dark:text-purple-300">Region</label>
                <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                  <SelectTrigger className="border-2 focus:border-purple-500">
                    <SelectValue placeholder="Select region" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Regions</SelectItem>
                    {regions.map(region => (
                      <SelectItem key={region} value={region}>{region}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block text-pink-700 dark:text-pink-300">Service Type</label>
                <Select value={selectedService} onValueChange={setSelectedService}>
                  <SelectTrigger className="border-2 focus:border-pink-500">
                    <SelectValue placeholder="Select service" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Services</SelectItem>
                    {uniqueServiceTypes.map(service => (
                      <SelectItem key={service} value={service}>{service}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-end">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setSearchTerm('')
                    setSelectedRegion('all')
                    setSelectedService('all')
                  }}
                  className="w-full border-2 border-orange-200 text-orange-700 hover:bg-orange-50"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <Card className="border-2">
          <CardHeader>
            <CardTitle className="text-xl">
              AWS Resources ({filteredServices.length})
            </CardTitle>
            <CardDescription>
              {filteredServices.length === services.length 
                ? `Showing all ${services.length} resources`
                : `Showing ${filteredServices.length} of ${services.length} resources`
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin mr-2" />
                <span>Scanning AWS resources...</span>
              </div>
            ) : filteredServices.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                {services.length === 0 ? 'No AWS resources found' : 'No resources match your filters'}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Service</TableHead>
                      <TableHead>Resource</TableHead>
                      <TableHead>Name/ID</TableHead>
                      <TableHead>Region</TableHead>
                      <TableHead>AZ</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Details</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredServices.map((service, index) => (
                      <TableRow key={index} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getServiceIcon(service.service_type) && (
                              <img 
                                src={getServiceIcon(service.service_type)} 
                                alt={`${service.service_type} icon`} 
                                className="w-6 h-6"
                              />
                            )}
                            <Badge className={serviceColors[service.service_type] || 'bg-gray-100 text-gray-800'}>
                              {service.service_type}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell className="font-medium">{service.resource_type}</TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium">{service.name}</div>
                            {service.name !== service.resource_id && (
                              <div className="text-sm text-muted-foreground">{service.resource_id}</div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{service.region}</Badge>
                        </TableCell>
                        <TableCell>{service.availability_zone}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(service.state)}>
                            {service.state}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm space-y-1">
                            {service.instance_type && (
                              <div>Type: {service.instance_type}</div>
                            )}
                            {service.engine && (
                              <div>Engine: {service.engine}</div>
                            )}
                            {service.runtime && (
                              <div>Runtime: {service.runtime}</div>
                            )}
                            {service.cidr_block && (
                              <div>CIDR: {service.cidr_block}</div>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App

