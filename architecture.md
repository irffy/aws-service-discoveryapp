# AWS Service Discovery Application - Architecture Design

## Overview
This application will scan all AWS regions and list all provisioned services across different regions and availability zones.

## Architecture

### Backend (Flask)
- **Framework**: Flask with CORS enabled
- **AWS Integration**: Boto3 SDK
- **Authentication**: AWS credentials (IAM user/role)
- **Port**: 5000 (listening on 0.0.0.0)

### Frontend (React)
- **Framework**: React with modern UI components
- **Styling**: CSS with responsive design
- **Features**: Interactive tables, filtering, search
- **Port**: 3000

### Key Components

#### Backend Endpoints
1. `GET /api/regions` - List all available AWS regions
2. `GET /api/services` - List all services across all regions
3. `GET /api/services/<region>` - List services in specific region
4. `GET /api/health` - Health check endpoint

#### AWS Services to Scan
1. **EC2**: Instances, Security Groups, Key Pairs, Volumes
2. **S3**: Buckets (global but with region info)
3. **RDS**: DB Instances, DB Clusters
4. **Lambda**: Functions
5. **VPC**: VPCs, Subnets, Internet Gateways, NAT Gateways
6. **ELB**: Load Balancers (ALB, NLB, CLB)
7. **CloudFormation**: Stacks
8. **IAM**: Roles, Users, Policies (global)
9. **Route53**: Hosted Zones (global)
10. **CloudWatch**: Alarms

#### Data Structure
```json
{
  "region": "us-east-1",
  "services": [
    {
      "service_type": "EC2",
      "resource_type": "Instance",
      "resource_id": "i-1234567890abcdef0",
      "name": "WebServer-1",
      "state": "running",
      "availability_zone": "us-east-1a",
      "tags": {...},
      "created_date": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## User Interface Design

### Main Dashboard
- **Header**: Application title and refresh button
- **Region Filter**: Dropdown to filter by region
- **Service Filter**: Dropdown to filter by service type
- **Search Bar**: Search by resource name or ID
- **Summary Cards**: Total resources by service type
- **Main Table**: Detailed list of all resources

### Table Columns
1. Service Type
2. Resource Type
3. Resource ID/Name
4. Region
5. Availability Zone
6. State/Status
7. Created Date
8. Tags (expandable)

### Features
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Refresh button to re-scan
- **Export**: Download results as CSV/JSON
- **Pagination**: Handle large datasets
- **Sorting**: Sort by any column
- **Filtering**: Multiple filter options

## Security Considerations
- AWS credentials should be configured via environment variables or IAM roles
- No hardcoded credentials in the application
- CORS properly configured for frontend-backend communication
- Input validation for all API endpoints

## Performance Optimization
- Parallel API calls to different regions
- Caching of results with TTL
- Progress indicators for long-running scans
- Pagination for large datasets

