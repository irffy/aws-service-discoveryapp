#!/bin/bash

# AWS Service Discovery Application - Quick Setup Script
# This script helps you quickly set up and run the AWS Service Discovery application

set -e

echo "🚀 AWS Service Discovery Application Setup"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.11 or later."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 20 or later."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Setup backend
echo ""
echo "📦 Setting up backend..."
cd aws-service-discovery

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing backend dependencies..."
source venv/Scripts/activate
pip install -r requirements.txt

echo "✅ Backend setup complete"

# Setup frontend
echo ""
echo "🎨 Setting up frontend..."
cd ../aws-service-discovery-frontend

# Install frontend dependencies
echo "Installing frontend dependencies..."
if command -v pnpm &> /dev/null; then
    pnpm install
else
    npm install --legacy-peer-deps
fi

echo "✅ Frontend setup complete"

# Check AWS credentials
echo ""
echo "🔐 Checking AWS credentials..."
cd ..

if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials are configured"
    aws sts get-caller-identity
else
    echo "⚠️  AWS credentials not found or not configured"
    echo ""
    echo "Please configure your AWS credentials using one of these methods:"
    echo "1. Run 'aws configure' and enter your credentials"
    echo "2. Set environment variables:"
    echo "   export AWS_ACCESS_KEY_ID=your_access_key"
    echo "   export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "   export AWS_DEFAULT_REGION=us-east-1"
    echo "3. Use IAM roles if running on EC2"
    echo ""
    echo "Required AWS permissions:"
    echo "- ec2:DescribeRegions, ec2:DescribeInstances, ec2:DescribeVpcs"
    echo "- rds:DescribeDBInstances"
    echo "- lambda:ListFunctions"
    echo "- s3:ListBuckets, s3:GetBucketLocation"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Start the backend:"
echo "   cd aws-service-discovery"
echo "   source venv/Scripts/activate"
echo "   python src/main.py"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd aws-service-discovery-frontend"
echo "   npm run dev  # or pnpm run dev"
echo ""
echo "3. Open http://localhost:5173 in your browser"
echo ""
echo "📚 For detailed instructions, see README.md"

