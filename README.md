# AWS Service Discovery Application

A comprehensive web application that scans all AWS regions and lists all provisioned services across different regions and availability zones.

## Features

- **Multi-Region Scanning**: Automatically scans all available AWS regions
- **Service Discovery**: Discovers EC2 instances, RDS databases, Lambda functions, S3 buckets, and VPCs
- **Real-time Filtering**: Filter by region, service type, or search by name/ID
- **Professional UI**: Modern, responsive design with dark/light mode support
- **Parallel Processing**: Concurrent scanning of multiple regions for faster results
- **Error Handling**: Comprehensive error handling and user feedback
- **Export Capabilities**: Ready for CSV/JSON export functionality

## Architecture

### Backend (Flask)
- **Framework**: Flask with CORS enabled
- **AWS Integration**: Boto3 SDK for AWS API calls
- **Endpoints**:
  - `GET /api/health` - Health check
  - `GET /api/regions` - List all AWS regions
  - `GET /api/services` - List all services across all regions
  - `GET /api/services/<region>` - List services in specific region
  - `GET /api/services/summary` - Get summary by region

### Frontend (React)
- **Framework**: React with modern UI components
- **Styling**: Tailwind CSS with shadcn/ui components
- **Features**: Interactive tables, filtering, search, responsive design

## Prerequisites

1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS Credentials**: Configured AWS credentials (see setup instructions below)
3. **Python 3.11+**: For the backend Flask application
4. **Node.js 20+**: For the frontend React application

## AWS Permissions Required

The application requires the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeRegions",
                "ec2:DescribeInstances",
                "ec2:DescribeVpcs",
                "rds:DescribeDBInstances",
                "lambda:ListFunctions",
                "s3:ListBuckets",
                "s3:GetBucketLocation"
            ],
            "Resource": "*"
        }
    ]
}
```

## Installation and Setup

### 1. Clone or Download the Application

```bash
# If using git
git clone <repository-url>
cd aws-service-discovery

# Or extract the provided files to a directory
```

### 2. Backend Setup

```bash
# Navigate to the backend directory
cd aws-service-discovery

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

Choose one of the following methods:

#### Method 1: AWS CLI Configuration
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

#### Method 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-east-1
```

#### Method 3: IAM Role (for EC2 instances)
If running on an EC2 instance, attach an IAM role with the required permissions.

### 4. Frontend Setup

```bash
# Navigate to the frontend directory
cd ../aws-service-discovery-frontend

# Install dependencies
npm install

# Or if using pnpm
pnpm install
```

## Running the Application

### 1. Start the Backend Server

```bash
cd aws-service-discovery
source venv/bin/activate
python src/main.py
```

The backend will be available at `http://localhost:5000`

### 2. Start the Frontend Server

```bash
cd aws-service-discovery-frontend
npm run dev

# Or if using pnpm
pnpm run dev
```

The frontend will be available at `http://localhost:5173`

### 3. Access the Application

Open your web browser and navigate to `http://localhost:5173`

## Usage

1. **Initial Load**: The application will automatically attempt to scan your AWS resources
2. **Refresh**: Click the "Refresh" button to re-scan all resources
3. **Filter by Region**: Use the region dropdown to filter resources by specific regions
4. **Filter by Service**: Use the service type dropdown to filter by EC2, RDS, Lambda, etc.
5. **Search**: Use the search box to find specific resources by name or ID
6. **Clear Filters**: Click "Clear Filters" to reset all filters

## Supported AWS Services

- **EC2**: Instances with state, instance type, and availability zone information
- **RDS**: Database instances with engine and status information
- **Lambda**: Functions with runtime and memory configuration
- **S3**: Buckets with region information
- **VPC**: Virtual Private Clouds with CIDR blocks and state

## Troubleshooting

### Common Issues

1. **"AWS credentials not configured"**
   - Ensure AWS credentials are properly configured using one of the methods above
   - Verify the credentials have the required permissions

2. **"Backend service is not available"**
   - Ensure the Flask backend is running on port 5000
   - Check for any error messages in the backend console

3. **"No regions available"**
   - This usually indicates AWS credentials are not configured or lack permissions
   - Verify your AWS credentials and permissions

4. **Slow loading**
   - The application scans all AWS regions, which can take time
   - Consider filtering by specific regions if you only need certain areas

### Debug Mode

To enable debug mode for more detailed error messages:

1. In the Flask backend, the debug mode is already enabled in development
2. Check the browser console for frontend errors
3. Check the Flask console for backend errors

## Security Considerations

- Never commit AWS credentials to version control
- Use IAM roles when possible instead of access keys
- Regularly rotate access keys
- Follow the principle of least privilege for IAM permissions
- Use environment variables or AWS credential files for credential storage

## Performance Optimization

- The application uses parallel processing to scan multiple regions simultaneously
- Results are cached temporarily to improve response times
- Consider implementing pagination for large numbers of resources

## Future Enhancements

- Export functionality (CSV, JSON)
- Resource tagging information
- Cost information integration
- Additional AWS services (CloudFormation, ELB, etc.)
- Real-time updates with WebSocket connections
- Resource grouping and organization features

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify AWS credentials and permissions
3. Check application logs for error messages
4. Ensure all dependencies are properly installed

## License

This application is provided as-is for educational and operational purposes.

