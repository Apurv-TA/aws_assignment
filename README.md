# aws_assignment
Tags used in this assignment are:
```
owner:    apurv.master@tigeranalytics.com
Name:     apurv_assignment
project:  aws-training
```
## Creating the flask app

In this part of the assignment we designed a web application using flask which can be used to display the list of files in given folder inside s3 bucket.

The result of folder creation on s3 bucket is shown in the below picture:
![aws_bucket](https://user-images.githubusercontent.com/93191532/163518830-ef7f2fe6-63cd-445b-bc08-86b4661d6b59.png)

After that we created an ec2 instance:

The security group inbound rules used while creating the instance are:
```
sgr-04dfe70845e75d0f5	8084	TCP	0.0.0.0/0
sgr-0d152190e1e6560d9	8085	TCP	0.0.0.0/0
sgr-0f19b40aed03c2a9e	8085	TCP	::/0
sgr-0428044e22f823c02	22	TCP	0.0.0.0/0
sgr-0f8abd0b9856028c2	5000	TCP	0.0.0.0/0
```

### Setting up the CLI
First of all we need to ssh to the ec2 instance using
```
ssh -i key_pair.pem ubuntu@ip
```
Then run the following:
```
sudo apt-get update
sudo apt-get install python3-venv
sudo apt-get install git
sudo apt-get install nginx
```

### Downloading the application and setting up the environment
```
git clone -b enh/issue#1/s3_ec2 https://github.com/Apurv-TA/aws_assignment.git
cd aws_assignment
python3 -m venv venv
source venv/bin/activate
pip install Flask
pip install boto3
pip install awscli
pip install gunicorn
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
WorkingDirectory=/home/ubuntu/aws_assignment
ExecStart=/home/ubuntu/aws_assignment/venv/bin/gunicorn -b localhost:8000 app:app
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

```
upstream flaskaws {
  server 127.0.0.1:8000;
}
server {
  listen 8085;
  root /aws_assignment/templates;
  
  location / {
    proxy_pass http://flaskaws;
   }
 }
```
Finally, we complete the hosting by running the command:
```
sudo systemctl restart nginx
```


## The output
### LOCAL EXECUTION
![Screenshot (100)](https://user-images.githubusercontent.com/93191532/164775079-32d5de6c-f3a2-4482-adfb-e3fa01760d35.png)

### To access the flask application these steps need to be followed:
- log in to the aws console<br>
  ![Screenshot (92)](https://user-images.githubusercontent.com/93191532/164647861-83fbf7af-83c1-438c-85de-d89d8359faa8.png)
- select the required role after logging in
- go to ec2 dashboard and select instances
  ![Screenshot (93)](https://user-images.githubusercontent.com/93191532/164645112-4989ca2b-48e7-4981-9dbf-d6cbf8cc8740.png)
- select apurv_assignment from the list of running instances if the instance is not running start it<br>
  ![Screenshot (97)](https://user-images.githubusercontent.com/93191532/164648256-96818893-0f23-4c09-b039-18b4e830893d.png)
- copy the public ipv4 address
  ![Screenshot (94)](https://user-images.githubusercontent.com/93191532/164648763-dc50fd27-b210-4adf-a04e-dee7de24f640.png)
- create a new tab and enter ip:8085 in the search pane where ip is the public ipv4 address
  ![Screenshot (95)](https://user-images.githubusercontent.com/93191532/164648572-52cf4fbb-dec1-44cb-a609-23fd6cca7b40.png)
- you can then view the flask application
  ![Screenshot (96)](https://user-images.githubusercontent.com/93191532/164648494-8a20cd0e-5b7d-4cc5-9a37-a9a0e3ef9fec.png)
