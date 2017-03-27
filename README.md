# VNG-Paul
Paul, the bot who will tell you which roster will win a vainglory match!

Players can ask questions on twitter and mention Paul(@vaingloryai), and Paul will then give his answer.

![Reply-Sample](https://github.com/devfans/VNG-Paul/blob/master/PaulsReply_Sample.png)


# setup
## prepare
First, install pip package tornado, Pillow and TwitterAPI
```
sudo pip install tornado
sudo pip install Pillow
sudo pip install TwitterAPI
```
Then register a twitter account and create an twitter application. When the twitter application is ready, you will have the api token and your secret, and you will also need to generate access token with post permission(for replying to players). Write these parameters in Paul.conf after you make a clone of the repo.

## clone and start
```
git clone https://github.com/devfans/VNG-Paul.git
cd VNG-Paul
./paul.py start
```

