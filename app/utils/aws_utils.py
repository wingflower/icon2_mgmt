import asyncio

from boto3 import Session
from starlette.responses import JSONResponse

REGION_DICT = {
    "ap-northeast-1": "Tokyo",
    "ap-northeast-2": "Seoul",
    "us-west-1": "N.California",
    "us-west-2": "Oregon",
    "us-east-1": "N.Virginia",
    "us-east-2": "Ohio",
    "ca-central-1": "Canada",
    "eu-west-1": "Ireland",
    "eu-west-2": "London",
    "eu-west-3": "Paris",
    "eu-central-1": "Frankfurt",
    "ap-southeast-1": "Singapore",
    "ap-southeast-2": "Sydney",
    "ap-south-1": "Mumbai",
    "sa-east-1": "São_Paulo",
    "ap-east-1": "Hongkong"
}

CITY_DICT = {
    "Tokyo": "ap-northeast-1",
    "Seoul": "ap-northeast-2",
    "N.California": "us-west-1",
    "Oregon": "us-west-2",
    "N.Virginia": "us-east-1",
    "Ohio": "us-east-2",
    "Canada": "ca-central-1",
    "Ireland": "eu-west-1",
    "London": "eu-west-2",
    "Paris": "eu-west-3",
    "Frankfurt": "eu-central-1",
    "Singapore": "ap-southeast-1",
    "Sydney": "ap-southeast-2",
    "Mumbai": "ap-south-1",
    "São_Paulo": "sa-east-1",
    "Hongkong": "ap-east-1"
}


def get_session(profile):
    session = Session(profile_name=profile)
    return session


def resource_all(session, *regions):
    resource_result = dict()
    for rg in regions:
        resource = session.resource('ec2', region_name=rg)
        resource_result[rg] = list(resource.instances.all())
    return resource_result


def instances_by_tags(session, **filters):
    instance_dict = dict()
    instance_list = list()
    filter_list = list()
    resource_result = resource_all(session)
    for key, val in filters.items():
        filter_list.append({'Key': key, 'Value': val})
    for rg, instances in resource_result.items():
        instance_dict[rg] = list()
        for instance in instances:
            _temp_list = [0 for i in range(len(filter_list))]
            for i, fd in enumerate(filter_list):
                if fd in instance.tags:
                    _temp_list[i] = 1
            if sum(_temp_list) == len(_temp_list):
                instance_dict[rg].append(instance)
                instance_list.append(instance)
    return {rg: instances for rg, instances in instance_dict.items() if instances}, instance_list


def instances_by_ids(session, rg_ids):
    instance_dict = dict()
    instance_list = list()
    for rg, ids in rg_ids.items():
        ec2_client = session.client('ec2', rg)
        res = ec2_client.describe_instances(
            InstanceIds=[id for id in ids]
        )
        instance_dict[rg] = res['Reservations'][0]['Instances'][0]
        instance_list.extend(res['Reservations'][0]['Instances'])
    return instance_dict, instance_list


def ec2_health_checker(session, instance_id, rg):
    ec2_client = session.client('ec2', rg)
    try:
        res = ec2_client.describe_instances(
            InstanceIds=[
                instance_id
            ]
        )['Reservations']
        return res[0]['Instances'][0]['State']['Name']
    except Exception as e:
        return e


def control_ec2(ec2_cmd, ec2_info, rg_ids):
    session = get_session(ec2_info.profile)
    instance_dict, _ = instances_by_ids(session, rg_ids)
    for rg, instances in instance_dict.items():
        for instance in instances:
            if instance.public_ip_address in ec2_info.ip_addr.split(','):
                ec2_client = session.client('ec2', rg)
                if ec2_cmd == 'start':
                    res = ec2_client.start_instances(
                        InstanceIds=[
                            instance.id,
                        ],
                    )
                elif ec2_cmd == 'stop':
                    res = ec2_client.stop_instances(
                        InstanceIds=[
                            instance.id,
                        ],
                    )


def control_elb(elb_cmd, elb_info, rg_ids):
    tg_name = None
    session = get_session(elb_info.profile)
    instance_dict, _ = instances_by_ids(session, rg_ids)
    for rg, instances in instance_dict.items():
        table_data = [
            ['Region', 'Name', 'ID', 'Public IP', 'Private IP', 'Port', 'State', 'Health', 'In/Out']
        ]
        temp_table = list()
        for instance in instances:
            i_name = None
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    i_name = tag["Value"]
            if instance.public_ip_address in elb_info.ip_addr.split(','):
                elbv2_client = session.client('elbv2', rg)
                elbsv2 = elbv2_client.describe_load_balancers()
                for elb in elbsv2['LoadBalancers']:
                    tgs = elbv2_client.describe_target_groups(LoadBalancerArn=elb['LoadBalancerArn'])
                    for tg in tgs['TargetGroups']:
                        if tg['TargetGroupName'] == tg_name:
                            tg_arn = tg['TargetGroupArn']
                            break
                if tg_arn:
                    if elb_cmd == 'add':
                        elbv2_client.register_targets(TargetGroupArn=tg_arn, Targets=[{'Id': instance.id}])
                    elif elb_cmd == 'rm':
                        elbv2_client.deregister_targets(TargetGroupArn=tg_arn, Targets=[{'Id': instance.id}])
                    elif elb_cmd == 'ls':
                        tg_health = elbv2_client.describe_target_health(TargetGroupArn=tg_arn)['TargetHealthDescriptions']
                        health_data = list()
                        health_cnt = None
                        for i, tg_h in enumerate(tg_health):
                            if tg_h['Target']['Id'] == instance.id:
                                temp_list = [
                                    rg,
                                    i_name,
                                    instance.id,
                                    instance.public_ip_address,
                                    instance.private_ip_address,
                                    tg_h['Target']['Port'],
                                    instance.state['Name'],
                                    tg_h['TargetHealth']['State'],
                                    'In'
                                ]
                                health_data.append(temp_list)
                                health_cnt = i
                                break
                            else:
                                temp_list = [
                                    rg,
                                    i_name,
                                    instance.id,
                                    instance.public_ip_address,
                                    instance.private_ip_address,
                                    'None',
                                    instance.state['Name'],
                                    'None',
                                    'Out'
                                ]
                                health_data.append(temp_list)
                        if health_data:
                            if health_cnt is None:
                                temp_table.append(health_data[0])
                            else:
                                temp_table.append(health_data[health_cnt])
        if elb_cmd == 'ls':
            temp_table = sorted(temp_table, key=lambda x:x[1])
            table_data.extend(temp_table)
            return table_data



def control_eip(eip_cmd, rg_ids):
    pass


def control_sg(sg_cmd, sg_info, rg_ids):
    pass


def control_s3(s3_cmd, rg_ids):
    pass