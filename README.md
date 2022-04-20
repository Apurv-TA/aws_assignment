# aws_assignment

## First part

In this part of the assignment we designed a web application using flask which can be used to display the list of files in given folder inside s3 bucket.

The result of folder creation on s3 bucket is shown in the below picture:
![aws_bucket](https://user-images.githubusercontent.com/93191532/163518830-ef7f2fe6-63cd-445b-bc08-86b4661d6b59.png)

After that we created an ec2 instance:<br>
The security group inbound rules used while creating the instance are:
```
sgr-04dfe70845e75d0f5	8084	TCP	0.0.0.0/0
sgr-0d152190e1e6560d9	8085	TCP	0.0.0.0/0
sgr-0f19b40aed03c2a9e	8085	TCP	::/0
sgr-0428044e22f823c02	22	TCP	0.0.0.0/0
sgr-0f8abd0b9856028c2	5000	TCP	0.0.0.0/0
```

Tags used while creation of the ec2 instance are:<br>
```
owner     apurv.master@tigeranalytics.com
Name      apurv_assignment
project   aws-training
```

### Setting up the CLI
<ol>
  <li>sudo apt-get update</li>
  <li>sudo apt-get install python3-venv</li>
  <li>sudo apt-get install git</li>
  <li>sudo apt-get install nginx</li>
</ol>

### Downloading the application and setting up the environment
<ol>
  <li>git clone -b enh/issue#1/s3_ec2 https://github.com/Apurv-TA/aws_assignment.git</li>
  <li>cd aws_assignment</li>
  <li>python3 -m venv venv</li>
  <li>source venv/bin/activate</li>
  <li>pip install Flask</li>
  <li>pip install boto3</li>
  <li>pip install awscli</li>
  <li>pip install gunicorn</li>
</ol>

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
<ol>
  <li>sudo systemctl daemon-reload</li>
  <li>sudo systemctl start aws_assignment.service</li>
  <li>sudo systemctl enable aws_assignment.service</li>
</ol>

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
> sudo systemctl restart nginx
