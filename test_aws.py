
# coding: utf-8

# In[1]:


class Vpc:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.elb_instances = []
        self.ec2_instances = []
        self.rds_instances = []

class Elb:
    
    def __init__(self, id, name, vpc_id):
        self.id = id
        self.name = name
        self.vpc_id = vpc_id
        self.security_group_instances = []
        
class Ec2:
    
    def __init__(self, id, name, vpc_id):
        self.id = id
        self.name = name
        self.vpc_id = vpc_id
        self.security_group_instances = []
        self.ebs_instances = []

class Security_Group:
    
    def __init__(self, id, name, vpc_id):
        self.id = id
        self.name = name
        self.vpc_id = vpc_id

class Ebs:
    
    def __init__(self, id, name, vpc_id, ec2_id):
        self.id = id
        self.name = name
        self.vpc_id = vpc_id
        self.ec2_id = ec2_id


# In[2]:


import json
f = open("vpc.json", "r")
s = f.read()
f.close()
vpcs = json.loads(s)


# In[3]:


global_vpc_dict = {}
for vpc in vpcs['Vpcs']:
    vpc_id = vpc["VpcId"]
    vpc_name = ""
    for tag in vpc['Tags']:
        if (tag["Key"] == "Name"):
            vpc_name = tag["Value"]
            break
    vpc_instance = Vpc(vpc_id, vpc_name)
    global_vpc_dict[vpc_id] = vpc_instance


# In[4]:


import jso
fn = open("elb.json", "r")
s = f.read()
f.close()
elbs = json.loads(s)


# In[5]:


for elb in elbs['LoadBalancerDescriptions']:
    elb_name = elb['LoadBalancerName']
    elb_id = elb_name
    vpc_id = elb['VPCId']
    elb_instance = Elb(elb_id, elb_name, vpc_id)
    
    security_group_id = elb['SecurityGroups'][0]
    security_group_name = security_group_id
    security_group_instance = Security_Group(security_group_id, security_group_name, vpc_id)
    elb_instance.security_group_instances.append(security_group_instance)
    vpc_instance = global_vpc_dict[vpc_id]
    vpc_instance.elb_instances.append(elb_instance)


# In[6]:


import json
f = open("elbv2.json", "r")
s = f.read()
f.close()
elbs = json.loads(s)


# In[7]:


for elb in elbs['LoadBalancers']:
    elb_name = elb['LoadBalancerName']
    elb_id = elb_name
    vpc_id = elb['VpcId']
    elb_instance = Elb(elb_id, elb_name, vpc_id)
    
    security_group_id = elb['SecurityGroups'][0]
    security_group_name = security_group_id
    security_group_instance = Security_Group(security_group_id, security_group_name, vpc_id)
    elb_instance.security_group_instances.append(security_group_instance)
    vpc_instance = global_vpc_dict[vpc_id]
    vpc_instance.elb_instances.append(elb_instance)


# In[8]:


f = open("ec2.json", "r")
s = f.read()
f.close()
ec2s = json.loads(s)


# In[9]:


global_ec2_dict = {}
for reservation in ec2s['Reservations']:
    for instance in reservation['Instances']:
        ec2_id = instance["InstanceId"]
        ec2_name = ""
        for tag in instance['Tags']:
            if (tag["Key"] == "Name"):
                ec2_name = tag["Value"]
                break 
        if (instance.get("VpcId")):
            vpc_id = instance["VpcId"]
    
            ec2_instance = Ec2(ec2_id, ec2_name, vpc_id)
            global_ec2_dict[ec2_id] = ec2_instance
            global_vpc_dict[vpc_id].ec2_instances.append(ec2_instance)
           
            security_group_id = instance['SecurityGroups'][0]['GroupId']
            security_group_name = instance['SecurityGroups'][0]['GroupName']
            security_group_instance = Security_Group(security_group_id, security_group_name, vpc_id)
            ec2_instance.security_group_instances.append(security_group_instance)
    
            for block_device in instance['BlockDeviceMappings']:
                ebs_id = block_device["Ebs"]["VolumeId"]
                ebs_name = block_device["DeviceName"]
                ebs_instance = Ebs(ebs_id, ebs_name, vpc_id, ec2_id)
                ec2_instance.ebs_instances.append(ebs_instance)
        else:
            print("*** Instance " + instance.get("InstanceId") + " does not belong to a VPC. ***")


# In[10]:


import operator

#
# Process each VPC
#
vpc_list = []
for vpc_instance in (sorted(global_vpc_dict.values(), key=operator.attrgetter('name'))):

    vpc_dict = { "id" : vpc_instance.id, "name" : vpc_instance.name }

    #
    # Process each ELB
    #
    elb_list = []
    for elb_instance in (sorted(vpc_instance.elb_instances, key=lambda x: x.name)):
        #
        # Process each security group
        #
        security_group_list = []
        for security_group_instance in (sorted(elb_instance.security_group_instances, key=lambda x: x.name)):
            security_group_id = security_group_instance.id
            security_group_name = security_group_instance.name
            security_group_dict = { "id" : security_group_id, "name" : security_group_name }
            security_group_list.append(security_group_dict)
            
        elb_dict = { "id" : elb_instance.id, "name" : elb_instance.name, "security_group_list" : security_group_list }
        elb_list.append(elb_dict)
            
    #
    # Process each EC2
    #
    ec2_list = []
    for ec2_instance in (sorted(vpc_instance.ec2_instances, key=lambda x: x.name)):
        #
        # Process each security group
        #
        security_group_list = []
        for security_group_instance in (sorted(ec2_instance.security_group_instances, key=lambda x: x.name)):
            security_group_id = security_group_instance.id
            security_group_name = security_group_instance.name
            security_group_dict = { "id" : security_group_id, "name" : security_group_name }
            security_group_list.append(security_group_dict)

        #
        # Process each EBS
        #
        ebs_list = []
        for ebs_instance in (sorted(ec2_instance.ebs_instances, key=lambda x: x.name)):
            ebs_dict = { "id" : ebs_instance.id, "name" : ebs_instance.name }
            ebs_list.append(ebs_dict)

        ec2_dict = { "id" : ec2_instance.id, "name" : ec2_instance.name, "security_group_list" : security_group_list, "ebs_list" : ebs_list }
        ec2_list.append(ec2_dict)
    
    vpc_dict["elb_list"] = elb_list
    vpc_dict["ec2_list"] = ec2_list
    vpc_list.append(vpc_dict)
    
aws_dict = {}
aws_dict["vpc_list"] = vpc_list

print(aws_dict)


# In[11]:


aws = json.dumps(aws_dict, indent=4)
print(aws)


# In[12]:


with open("aws.json", "w") as f:
    f.write(aws)
    f.close()


# In[13]:


s/aws$ jupyter notebookimport operator

from treelib import Tree, Node

tree = Tree()
root_node = tree.create_node("VPCs","root_node")
        
#
# Process each VPC
#
for vpc_instance in (sorted(global_vpc_dict.values(), key=operator.attrgetter('name'))):

    vpc_node_label = "VPC: " + vpc_instance.name + " (" + vpc_instance.id + ")"
    vpc_node = Node(vpc_node_label, vpc_instance.id)
    tree.add_node(vpc_node, "root_node")

    #
    # Process each ELB
    #
    for elb_instance in (sorted(vpc_instance.elb_instances, key=lambda x: x.name)):
        elb_node_label = "ELB: " + elb_instance.name
        elb_node = Node(elb_node_label, elb_instance.id)
        tree.add_node(elb_node, vpc_instance.id)
        #
        # Process each security group
        #
        for security_group_instance in (sorted(elb_instance.security_group_instances, key=lambda x: x.name)):
            security_group_id = security_group_instance.id
            security_group_name = security_group_instance.name
            security_group_node_label = "Security Group: " + security_group_name + " (" + security_group_id + ")"
            security_group_node_id = elb_instance.id + ":" + security_group_id
            security_group_node = Node(security_group_node_label, security_group_node_id)
            tree.add_node(security_group_node, elb_instance.id)
    
    #
    # Process each EC2
    #
    for ec2_instance in (sorted(vpc_instance.ec2_instances, key=lambda x: x.name)):
        ec2_node_label = "EC2: " + ec2_instance.name + " (" + ec2_instance.id + ")"
        ec2_node = Node(ec2_node_label, ec2_instance.id)
        tree.add_node(ec2_node, vpc_instance.id)
        #
        # Process each security group
        #
        for security_group_instance in (sorted(ec2_instance.security_group_instances, key=lambda x: x.name)):
            security_group_id = security_group_instance.id
            security_group_name = security_group_instance.name
            security_group_node_label = "Security Group: " + security_group_name + " (" + security_group_id + ")"
            security_group_node_id = ec2_instance.id + ":" + security_group_id
            security_group_node = Node(security_group_node_label, security_group_node_id)
            tree.add_node(security_group_node, ec2_instance.id)
        #
        # Process each EBS
        #
        for ebs_instance in (sorted(ec2_instance.ebs_instances, key=lambda x: x.name)):
            ebs_id = ebs_instance.id
            ebs_name = ebs_instance.name
            ebs_node_label = "EBS: " + ebs_name + " (" + ebs_id + ")"
            ebs_node_id = ec2_instance.id + ":" + ebs_id
            ebs_node = Node(ebs_node_label, ebs_node_id)
            tree.add_node(ebs_node, ec2_instance.id)


# In[14]:


tree.show("root_node",0,1)

