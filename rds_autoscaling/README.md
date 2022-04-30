# aws_assignment

Tags used in this assignment are:
```
owner:    apurv.master@tigeranalytics.com
project:  aws-training
```
## Setting up the VPC
1. Configuration of the VPC and the subnets are:\
    ```
    # Apurv_VPC
    IPV4 CIDR:  10.0.0.0/16

    # Apurv_Private
    CIDR:		10.0.1.0/24
    AZ:		us-east-1a

    # Apurv_Public
    CIDR:		10.0.2.0/24
    AZ:		us-east-1b
    ```
2. Create and attach an IG(Internet Gateway) to the VPC.
3. Create custom route table for both private and public subnets. Attach IG to public route table.

## Creating the EC2 instance
We created an EC2 instance on public subnet of the VPC.

The security group used is given below:
  ```
  sgr-007810a52495af763	22	TCP	0.0.0.0/0
  sgr-0980174db23442166	80	TCP	0.0.0.0/0
  sgr-0aca493d4ece9e4f8	80	TCP	::/0
  ```

## Setting up RDS 
1. Create a security group for the Aurora MySQL
  ```
  IPv4	MYSQL/Aurora	TCP	3306	10.0.2.0/24
  IPv4	MYSQL/Aurora	TCP	3306	0.0.0.0/0
  IPv4	MYSQL/Aurora	TCP	3306	106.212.44.56/32
  ```
2. Provision a Aurora MySQL instance in the private subnet of created VPC and add the security group created.

## Setting up CLI
First of all we need to ssh to the ec2 instance using
```
chmod 400 ec2_assignment1.pem
ssh -i ec2_assignment1.pem ubuntu@public_ipv4
```
Then run the following:
```
sudo apt-get update
sudo apt-get install python3-venv
sudo apt-get install git
sudo apt-get install nginx
sudo apt-get install mysql-server
```
Check the connectivity with RDS by running
```
mysql -uadmin -hapurv-database-cluster-instance-1.cldb1lgd5bay.us-east-1.rds.amazonaws.com -p
```
## Set up the database:
```
use apurv_database;
create table logs (access_time DATETIME, message VARCHAR(10));
```
## Setting up the flaks application
### Downloading the application and setting up the environment
```
git clone -b BRANCH-NAME GIT-DOWNLOAD-LINK

cd repo_name
git checkout -b enh/issue#2/rds_autoscaling
python3 -m venv venv
source venv/bin/activate

pip install flask
pip install boto3
pip install awscli
pip install gunicorn
python -m pip install mysql-connector-python
pip install mysql.connector
```
### Setting up gunicorn
Opening up and creating service file -> sudo nano /etc/systemd/system/aws_assignment.service
```
[Unit]
Description=Gunicorn instance for a simple Flask app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/aws_assignment/rds_autoscaling
ExecStart=/home/ubuntu/aws_assignment/rds_autoscaling/venv/bin/gunicorn -b localhost:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl daemon-reload
sudo systemctl start aws_assignment.service
sudo systemctl enable aws_assignment.service
```
### Setting up nginx
Opening up and creating service file -> sudo nano /etc/nginx/sites-available/default

We are setting up nginx with the default setting i.e. port 80, these lines of code are added to the default file
```
upstream flaskaws {
    server 127.0.0.1:8000;
}

# Some code above
location / {
    proxy_pass http://flaskaws;
}
# some code below
```
Finally, we complete the hosting by running the command:
```
sudo systemctl restart nginx
```

### The output of the application is shown below:
![Screenshot (104)](https://user-images.githubusercontent.com/93191532/166095195-109f714c-747e-4bbc-b37e-42a3e3fb1846.png)


## Provision an AWS Application load balancer which connects to the Autoscaling group.

The initial steps taken are:

1. Create a launch template using an image of the instance and use the security group created in the first part.
2. Create a target group using the initial EC2 intance.

### Creating the autoscaling group

Create an autoscaling group using the created launch template and the VPC. Also, select the `Attach new load balancer` radio button and load balancer type as `Application load balancer`.

### Load balancer

1. Select load balancer scheme as `internet-facing`.
2. Select the VPC and availability zones same as per the instance we have created earlier.
3. In listener and routing select the target group which we have created earlier.
4. In group size we have selected desired capacity as 0, minimum capacity as 0 and maximum capacity as 3.

### Using the DNS name of the load balance our output is:
![Screenshot (105)](https://user-images.githubusercontent.com/93191532/166095210-76b155a6-8ab5-46d1-8df9-39218143ea19.png)

## Creating the lambda function

Now we have to create a Lambda function which scales down the autoscaling group to zero on every Saturday and scales up to 2 on every Monday morning.

For this purpose we have created two lambda functions one to start the ASG and the other to stop it. The code used in both of them is the same and the difference being different Trigger events and Environement Variables

Code is
```import os
import boto3

client = boto3.client('autoscaling')

def get_env_variable(var_name):
    return os.environ[var_name]



def lambda_handler(event, context):
    auto_scaling_groups = get_env_variable('NAMES').split()

    for group in auto_scaling_groups:
        if servers_need_to_be_started(group):
            action = "Starting"
            min_size = int(get_env_variable('MIN_SIZE'))
            max_size = int(get_env_variable('MAX_SIZE'))
            desired_capacity = int(get_env_variable('DESIRED_CAPACITY'))
        else:
            action = "Stopping"
            min_size = 0
            max_size = 0
            desired_capacity = 0

        print(action + ": " + group)
        response = client.update_auto_scaling_group(
            AutoScalingGroupName=group,
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=desired_capacity,
        )

        print(response)

def servers_need_to_be_started(group_name):
    min_group_size = get_current_min_group_size(group_name)
    if min_group_size == 0:
        return True
    else:
        return False

def get_current_min_group_size(group_name):
    response = client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[ group_name ],
    )
    return response["AutoScalingGroups"][0]["MinSize"]
```
The two `EventBridge(CloudWatch Events)` that triggers the configuration is shown below:
```
Create a new rule of "Schedule expression type"

Create two triggers:

apurv_autoscale_weekday
Corn Expression:  corn(00 00 ? * MON-FRI *)

apurv_autoscale_weekend
Corn expression:  corn(00 00 ? * SAT-SUN *)
```


The Emviroment variables are
```
  `NAMES` - Space separated list of the Auto Scaling Groups you want to manage with this function
  `MIN_SIZE` - Minimum size of the Auto Scaling Group(s) when EC2 instances are started
  `MAX_SIZE` - Maximum size of the Auto Scaling Group(s) when EC2 instances are started
  `DESIRED_CAPACITY` - Desired capacity of the Auto Scaling Group(s) when EC2 instances are started
  
  apurv_autoscale_weekday
  DESIRED_CAPACITY	2
  MAX_SIZE	3
  MIN_SIZE	0
  NAMES	Apurv-ASG

  apurv_autoscale_weekend
  DESIRED_CAPACITY	0
  MAX_SIZE	0
  MIN_SIZE	0
  NAMES	Apurv-ASG
```
The custom role attached to both the lambda functions have this policy:
  ```
  {
    "Effect": "Allow",
    "Action": "autoscaling:*",
    "Resource": "*"
   }
  ```
  
The function can be tested by hitting the `Test` button. The first time an `Input test event` popup will appear. For `Sample event template` select `Scheduled event` and click `Save and test`.
### The output of lambda function is
![Screenshot (106)](https://user-images.githubusercontent.com/93191532/166096322-579b7825-9498-4059-8e34-5a5a5099bc29.png)


# Final output
To access the flaks app these steps need to be taken:
- log in to the aws console<br>
![Screenshot (92)](https://user-images.githubusercontent.com/93191532/166096904-50b1daba-29ee-4d2c-aa9c-b4f36f7af5c2.png)
- select the required role after logging in
- Got to ec2 dashboard and select Load Balancers
![Screenshot (93)](https://user-images.githubusercontent.com/93191532/166096967-80567415-53cb-4b4b-a0de-0314ccd77fe2.png)
- Select `Apurv-LB` and copy the DNS name
![Screenshot (107)](https://user-images.githubusercontent.com/93191532/166097017-a0bfe7a5-ad57-407d-b17d-4941a03d6d20.png)
- Enter a new tab and enter the DNS name along with http protocol
![Screenshot (109)](https://user-images.githubusercontent.com/93191532/166097063-e169d232-6063-4c81-99c8-e17695f1d5ea.png)
- You can then view the Flask application
![Screenshot (105)](https://user-images.githubusercontent.com/93191532/166097077-3fa2dd8b-3ddc-43fa-a8a1-e6e1d4b1307a.png)
