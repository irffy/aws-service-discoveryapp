from flask import Blueprint, jsonify, request
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import concurrent.futures
from datetime import datetime
import json

aws_bp = Blueprint('aws', __name__)

def get_all_regions():
    """Get all available AWS regions"""
    try:
        ec2 = boto3.client('ec2', region_name='us-east-1')
        response = ec2.describe_regions()
        return [region['RegionName'] for region in response['Regions']]
    except Exception as e:
        print(f"Error getting regions: {str(e)}")
        return []

def scan_ec2_instances(region):
    """Scan EC2 instances in a specific region"""
    resources = []
    try:
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_instances()
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                name = 'N/A'
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                
                resources.append({
                    'service_type': 'EC2',
                    'resource_type': 'Instance',
                    'resource_id': instance['InstanceId'],
                    'name': name,
                    'state': instance['State']['Name'],
                    'region': region,
                    'availability_zone': instance.get('Placement', {}).get('AvailabilityZone', 'N/A'),
                    'instance_type': instance.get('InstanceType', 'N/A'),
                    'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else 'N/A',
                    'tags': instance.get('Tags', [])
                })
    except Exception as e:
        print(f"Error scanning EC2 in {region}: {str(e)}")
    
    return resources

def scan_rds_instances(region):
    """Scan RDS instances in a specific region"""
    resources = []
    try:
        rds = boto3.client('rds', region_name=region)
        response = rds.describe_db_instances()
        
        for db_instance in response['DBInstances']:
            resources.append({
                'service_type': 'RDS',
                'resource_type': 'DB Instance',
                'resource_id': db_instance['DBInstanceIdentifier'],
                'name': db_instance['DBInstanceIdentifier'],
                'state': db_instance['DBInstanceStatus'],
                'region': region,
                'availability_zone': db_instance.get('AvailabilityZone', 'N/A'),
                'instance_type': db_instance.get('DBInstanceClass', 'N/A'),
                'engine': db_instance.get('Engine', 'N/A'),
                'created_time': db_instance.get('InstanceCreateTime', '').isoformat() if db_instance.get('InstanceCreateTime') else 'N/A',
                'tags': []
            })
    except Exception as e:
        print(f"Error scanning RDS in {region}: {str(e)}")
    
    return resources

def scan_lambda_functions(region):
    """Scan Lambda functions in a specific region"""
    resources = []
    try:
        lambda_client = boto3.client('lambda', region_name=region)
        response = lambda_client.list_functions()
        
        for function in response['Functions']:
            resources.append({
                'service_type': 'Lambda',
                'resource_type': 'Function',
                'resource_id': function['FunctionName'],
                'name': function['FunctionName'],
                'state': function.get('State', 'N/A'),
                'region': region,
                'availability_zone': 'N/A',
                'runtime': function.get('Runtime', 'N/A'),
                'memory_size': function.get('MemorySize', 'N/A'),
                'last_modified': function.get('LastModified', 'N/A'),
                'tags': []
            })
    except Exception as e:
        print(f"Error scanning Lambda in {region}: {str(e)}")
    
    return resources

def scan_s3_buckets():
    """Scan S3 buckets (global service)"""
    resources = []
    try:
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        
        for bucket in response['Buckets']:
            # Get bucket region
            try:
                location_response = s3.get_bucket_location(Bucket=bucket['Name'])
                region = location_response['LocationConstraint'] or 'us-east-1'
            except:
                region = 'unknown'
            
            resources.append({
                'service_type': 'S3',
                'resource_type': 'Bucket',
                'resource_id': bucket['Name'],
                'name': bucket['Name'],
                'state': 'Active',
                'region': region,
                'availability_zone': 'N/A',
                'created_date': bucket.get('CreationDate', '').isoformat() if bucket.get('CreationDate') else 'N/A',
                'tags': []
            })
    except Exception as e:
        print(f"Error scanning S3: {str(e)}")
    
    return resources

def scan_vpcs(region):
    """Scan VPCs in a specific region"""
    resources = []
    try:
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_vpcs()
        
        for vpc in response['Vpcs']:
            name = 'N/A'
            if 'Tags' in vpc:
                for tag in vpc['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
            
            resources.append({
                'service_type': 'VPC',
                'resource_type': 'VPC',
                'resource_id': vpc['VpcId'],
                'name': name,
                'state': vpc['State'],
                'region': region,
                'availability_zone': 'N/A',
                'cidr_block': vpc.get('CidrBlock', 'N/A'),
                'is_default': vpc.get('IsDefault', False),
                'tags': vpc.get('Tags', [])
            })
    except Exception as e:
        print(f"Error scanning VPCs in {region}: {str(e)}")
    
    return resources

def scan_region(region):
    """Scan all services in a specific region"""
    all_resources = []
    
    # Scan regional services
    all_resources.extend(scan_ec2_instances(region))
    all_resources.extend(scan_rds_instances(region))
    all_resources.extend(scan_lambda_functions(region))
    all_resources.extend(scan_vpcs(region))
    
    return all_resources

@aws_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@aws_bp.route('/regions', methods=['GET'])
def get_regions():
    """Get all available AWS regions"""
    try:
        regions = get_all_regions()
        return jsonify({'regions': regions, 'count': len(regions)})
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not configured'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@aws_bp.route('/services', methods=['GET'])
def get_all_services():
    """Get all services across all regions"""
    try:
        regions = get_all_regions()
        if not regions:
            return jsonify({'error': 'No regions available'}), 500
        
        all_resources = []
        
        # Add S3 buckets (global service)
        all_resources.extend(scan_s3_buckets())
        
        # Scan all regions in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_region = {executor.submit(scan_region, region): region for region in regions}
            
            for future in concurrent.futures.as_completed(future_to_region):
                region = future_to_region[future]
                try:
                    region_resources = future.result()
                    all_resources.extend(region_resources)
                except Exception as e:
                    print(f"Error scanning region {region}: {str(e)}")
        
        # Group by service type for summary
        service_summary = {}
        for resource in all_resources:
            service_type = resource['service_type']
            if service_type not in service_summary:
                service_summary[service_type] = 0
            service_summary[service_type] += 1
        
        return jsonify({
            'resources': all_resources,
            'total_count': len(all_resources),
            'service_summary': service_summary,
            'regions_scanned': len(regions),
            'timestamp': datetime.now().isoformat()
        })
        
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not configured'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@aws_bp.route('/services/<region>', methods=['GET'])
def get_services_by_region(region):
    """Get all services in a specific region"""
    try:
        resources = scan_region(region)
        
        # Add S3 buckets for the specific region
        s3_buckets = scan_s3_buckets()
        region_s3_buckets = [bucket for bucket in s3_buckets if bucket['region'] == region]
        resources.extend(region_s3_buckets)
        
        service_summary = {}
        for resource in resources:
            service_type = resource['service_type']
            if service_type not in service_summary:
                service_summary[service_type] = 0
            service_summary[service_type] += 1
        
        return jsonify({
            'region': region,
            'resources': resources,
            'total_count': len(resources),
            'service_summary': service_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not configured'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@aws_bp.route('/services/summary', methods=['GET'])
def get_services_summary():
    """Get a summary of services by region"""
    try:
        regions = get_all_regions()
        if not regions:
            return jsonify({'error': 'No regions available'}), 500
        
        region_summary = {}
        
        # Scan all regions in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_region = {executor.submit(scan_region, region): region for region in regions}
            
            for future in concurrent.futures.as_completed(future_to_region):
                region = future_to_region[future]
                try:
                    region_resources = future.result()
                    
                    service_counts = {}
                    for resource in region_resources:
                        service_type = resource['service_type']
                        if service_type not in service_counts:
                            service_counts[service_type] = 0
                        service_counts[service_type] += 1
                    
                    region_summary[region] = {
                        'total_resources': len(region_resources),
                        'service_counts': service_counts
                    }
                except Exception as e:
                    print(f"Error scanning region {region}: {str(e)}")
                    region_summary[region] = {
                        'total_resources': 0,
                        'service_counts': {},
                        'error': str(e)
                    }
        
        # Add S3 summary (global)
        s3_buckets = scan_s3_buckets()
        s3_by_region = {}
        for bucket in s3_buckets:
            region = bucket['region']
            if region not in s3_by_region:
                s3_by_region[region] = 0
            s3_by_region[region] += 1
        
        # Add S3 counts to region summary
        for region, count in s3_by_region.items():
            if region in region_summary:
                if 'S3' not in region_summary[region]['service_counts']:
                    region_summary[region]['service_counts']['S3'] = 0
                region_summary[region]['service_counts']['S3'] += count
                region_summary[region]['total_resources'] += count
        
        return jsonify({
            'region_summary': region_summary,
            'total_regions': len(regions),
            'timestamp': datetime.now().isoformat()
        })
        
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not configured'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

