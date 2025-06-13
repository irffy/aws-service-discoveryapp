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

def scan_elb_load_balancers(region):
    """Scan ELB Load Balancers in a specific region"""
    resources = []
    try:
        # Application and Network Load Balancers
        elbv2 = boto3.client('elbv2', region_name=region)
        response = elbv2.describe_load_balancers()
        for lb in response['LoadBalancers']:
            resources.append({
                'service_type': 'ELB',
                'resource_type': f"{lb['Type'].title()} Load Balancer",
                'resource_id': lb['LoadBalancerName'],
                'name': lb['LoadBalancerName'],
                'state': lb['State']['Code'],
                'region': region,
                'availability_zone': ', '.join([az['ZoneName'] for az in lb.get('AvailabilityZones', [])]),
                'scheme': lb.get('Scheme', 'N/A'),
                'vpc_id': lb.get('VpcId', 'N/A'),
                'created_time': lb.get('CreatedTime', '').isoformat() if lb.get('CreatedTime') else 'N/A',
                'tags': []
            })
    except Exception as e:
        print(f"Error scanning ELBv2 in {region}: {str(e)}")
    return resources

def scan_cloudformation_stacks(region):
    """Scan CloudFormation stacks in a specific region"""
    resources = []
    try:
        cf = boto3.client('cloudformation', region_name=region)
        response = cf.describe_stacks()
        
        for stack in response['Stacks']:
            resources.append({
                'service_type': 'CloudFormation',
                'resource_type': 'Stack',
                'resource_id': stack['StackName'],
                'name': stack['StackName'],
                'state': stack['StackStatus'],
                'region': region,
                'availability_zone': 'N/A',
                'creation_time': stack.get('CreationTime', '').isoformat() if stack.get('CreationTime') else 'N/A',
                'template_description': stack.get('Description', 'N/A'),
                'tags': stack.get('Tags', [])
            })
    except Exception as e:
        print(f"Error scanning CloudFormation in {region}: {str(e)}")
    
    return resources

def scan_ecs_clusters(region):
    """Scan ECS clusters in a specific region"""
    resources = []
    try:
        ecs = boto3.client('ecs', region_name=region)
        
        # List clusters
        cluster_response = ecs.list_clusters()
        if cluster_response['clusterArns']:
            # Describe clusters
            describe_response = ecs.describe_clusters(clusters=cluster_response['clusterArns'])
            
            for cluster in describe_response['clusters']:
                resources.append({
                    'service_type': 'ECS',
                    'resource_type': 'Cluster',
                    'resource_id': cluster['clusterName'],
                    'name': cluster['clusterName'],
                    'state': cluster['status'],
                    'region': region,
                    'availability_zone': 'N/A',
                    'running_tasks': cluster.get('runningTasksCount', 0),
                    'pending_tasks': cluster.get('pendingTasksCount', 0),
                    'active_services': cluster.get('activeServicesCount', 0),
                    'tags': cluster.get('tags', [])
                })
    except Exception as e:
        print(f"Error scanning ECS in {region}: {str(e)}")
    
    return resources

def scan_sns_topics(region):
    """Scan SNS topics in a specific region"""
    resources = []
    try:
        sns = boto3.client('sns', region_name=region)
        response = sns.list_topics()
        
        for topic in response['Topics']:
            topic_arn = topic['TopicArn']
            topic_name = topic_arn.split(':')[-1]
            
            # Get topic attributes
            try:
                attrs_response = sns.get_topic_attributes(TopicArn=topic_arn)
                attributes = attrs_response['Attributes']
                
                resources.append({
                    'service_type': 'SNS',
                    'resource_type': 'Topic',
                    'resource_id': topic_name,
                    'name': topic_name,
                    'state': 'Active',
                    'region': region,
                    'availability_zone': 'N/A',
                    'subscriptions_confirmed': attributes.get('SubscriptionsConfirmed', '0'),
                    'subscriptions_pending': attributes.get('SubscriptionsPending', '0'),
                    'display_name': attributes.get('DisplayName', 'N/A'),
                    'tags': []
                })
            except Exception as e:
                print(f"Error getting SNS topic attributes for {topic_name}: {str(e)}")
                
    except Exception as e:
        print(f"Error scanning SNS in {region}: {str(e)}")
    
    return resources

def scan_sqs_queues(region):
    """Scan SQS queues in a specific region"""
    resources = []
    try:
        sqs = boto3.client('sqs', region_name=region)
        response = sqs.list_queues()
        
        if 'QueueUrls' in response:
            for queue_url in response['QueueUrls']:
                queue_name = queue_url.split('/')[-1]
                
                # Get queue attributes
                try:
                    attrs_response = sqs.get_queue_attributes(
                        QueueUrl=queue_url,
                        AttributeNames=['All']
                    )
                    attributes = attrs_response['Attributes']
                    
                    resources.append({
                        'service_type': 'SQS',
                        'resource_type': 'Queue',
                        'resource_id': queue_name,
                        'name': queue_name,
                        'state': 'Active',
                        'region': region,
                        'availability_zone': 'N/A',
                        'messages_available': attributes.get('ApproximateNumberOfMessages', '0'),
                        'messages_in_flight': attributes.get('ApproximateNumberOfMessagesNotVisible', '0'),
                        'created_timestamp': attributes.get('CreatedTimestamp', 'N/A'),
                        'tags': []
                    })
                except Exception as e:
                    print(f"Error getting SQS queue attributes for {queue_name}: {str(e)}")
                    
    except Exception as e:
        print(f"Error scanning SQS in {region}: {str(e)}")
    
    return resources

def scan_dynamodb_tables(region):
    """Scan DynamoDB tables in a specific region"""
    resources = []
    try:
        dynamodb = boto3.client('dynamodb', region_name=region)
        response = dynamodb.list_tables()
        
        for table_name in response['TableNames']:
            # Get table details
            try:
                table_response = dynamodb.describe_table(TableName=table_name)
                table = table_response['Table']
                
                resources.append({
                    'service_type': 'DynamoDB',
                    'resource_type': 'Table',
                    'resource_id': table_name,
                    'name': table_name,
                    'state': table['TableStatus'],
                    'region': region,
                    'availability_zone': 'N/A',
                    'item_count': table.get('ItemCount', 0),
                    'table_size_bytes': table.get('TableSizeBytes', 0),
                    'billing_mode': table.get('BillingModeSummary', {}).get('BillingMode', 'N/A'),
                    'created_time': table.get('CreationDateTime', '').isoformat() if table.get('CreationDateTime') else 'N/A',
                    'tags': []
                })
            except Exception as e:
                print(f"Error getting DynamoDB table details for {table_name}: {str(e)}")
                
    except Exception as e:
        print(f"Error scanning DynamoDB in {region}: {str(e)}")
    
    return resources

def scan_region(region):
    """Scan all services in a specific region"""
    all_resources = []
    
    # Scan regional services
    all_resources.extend(scan_ec2_instances(region))
    all_resources.extend(scan_rds_instances(region))
    all_resources.extend(scan_lambda_functions(region))
    all_resources.extend(scan_vpcs(region))
    all_resources.extend(scan_elb_load_balancers(region))
    all_resources.extend(scan_cloudformation_stacks(region))
    all_resources.extend(scan_ecs_clusters(region))
    all_resources.extend(scan_sns_topics(region))
    all_resources.extend(scan_sqs_queues(region))
    all_resources.extend(scan_dynamodb_tables(region))
    
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
