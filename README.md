# card_game_28

## Webserver setup in an EC2 instance
Login: ssh -i ~/.ssh/<ec2>.pem ubuntu@<ec2 instance ip>

### Commands
sudo apt-get update

sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3

sudo pip3 install virtualenv

mkdir -p card_game_28/django

cd card_game_28/django

virtualenv env

source ../env/bin/activate

git clone https://github.com/sudhiir1/card_game_28.git

cd card_game_28

pip3 install -r requirements.txt
