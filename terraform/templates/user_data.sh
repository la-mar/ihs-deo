#!/bin/bash

sudo apt-get update
sudo apt-get install jq -y
# sudo apt install awscli -y


# echo "Configuring awscli..."
# aws configure set aws_access_key_id $(curl --silent http://169.254.169.254/latest/meta-data/iam/security-credentials/ecs-collector-cluster-prod-ecs-instance | jq -r '.AccessKeyId')
# aws configure set aws_secret_access_key $(curl --silent http://169.254.169.254/latest/meta-data/iam/security-credentials/ecs-collector-cluster-prod-ecs-instance | jq -r '.SecretAccessKey')
# aws configure set region $(curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')




echo "Mounting EBS volumes..."

function test_volume_mounted
{
    value=$(df -h |grep /dev/nvme1n1)
    echo $?
}
result="1"

while [ $result -eq 1 ]
do
DEVICE=/dev/nvme1n1
MOUNT_POINT=/data
FSTYPE=xfs
echo "Creating file system on $DEVICE"
mkfs -t $FSTYPE $DEVICE
mkdir $MOUNT_POINT
mount $DEVICE $MOUNT_POINT
result=$(test_volume_mounted)
echo $result
sleep 10
done

# Add an entry to /etc/fstab to make the EBS volume remount after a restart
echo "Writing mount entry to fstab..."
UUID=$(sudo blkid -s UUID -o value /dev/nvme1n1)
# FSTYPE=$(sudo blkid -s TYPE -o value /dev/nvme1n1)
echo "UUID=$UUID $MOUNT_POINT $FSTYPE defaults 0 2" | sudo tee -a /etc/fstab


echo "Installing Datadog Agent..."
DD_API_KEY=${dd_api_key} bash -c "$(curl -L https://raw.githubusercontent.com/DataDog/datadog-agent/master/cmd/agent/install_script.sh)"


########## Install MongoDB ##########

# Mongo Install Reference:  https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
echo "Installing MongoDB resources..."

wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -

# Create a list file for MongoDB
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list

# Reload local package database
sudo apt-get update

# Install the MongoDB packages.
sudo apt-get install -y mongodb-org

mkdir /data/db
chown mongodb /data/db
service mongod start
sleep 5

cat > /etc/mongod.conf <<- EOF
# mongod.conf

# for documentation of all options, see:
#   http://docs.mongodb.org/manual/reference/configuration-options/

# Where and how to store data.
storage:
#  dbPath: /data/db
  journal:
    enabled: true
#  engine:
#  mmapv1:
#  wiredTiger:

# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

# network interfaces
net:
  port: 27017
  bindIp: 0.0.0.0


# how the process runs
processManagement:
  timeZoneInfo: /usr/share/zoneinfo

security:
  authorization: 'enabled'

#operationProfiling:

#replication:

#sharding:

EOF

echo "Creating admin user"
mongo admin <<- EOF
use admin
var user = {
  "user" : "${db_username}",
  "pwd" : "${db_password}",
  roles : [
              { role: "userAdminAnyDatabase", db: "admin" },
              { role: "readWriteAnyDatabase", db: "admin" },
              { role: "dbAdminAnyDatabase", db: "admin" },
              { role: "clusterAdmin", db: "admin" }
           ]
}
db.createUser(user);
exit
EOF


service mongod restart


echo "Enabling mongod.service to start on boot"
sudo systemctl enable mongod




















