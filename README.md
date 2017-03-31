# Overview
VaingloryAI is the chatbot that tells you who will win in any possible Vainglory match! Players can @VaingloryAI and find out answers for an array of questions. You can ask about hero vs hero, player vs player, or team vs team, or any combination of heroes and players. This is a fun way for players to see who is better and challenge their friends or guildmates!
Visit @VaingloryAI on Twitter to try it out!

<p align="center">
  <img src="https://raw.githubusercontent.com/devfans/VaingloryAI/master/misc/vai_photo.jpg" alt="Sublime's custom image" width="200" height="200"/>
</p>


# Functionality
Players @ message the Twitter account with their query. There are 5 types of queries: hero vs hero, hero team vs hero team, player vs player, player team vs player team (not actual Vainglory Teams yet), or a mixture of players and heroes. Queries are structured as follows:
@VaingloryAI Vox vs Ozo
@VaingloryAI Vox+Ardan+Celeste vs Ozo+Taka+Krul
@VaingloryAI player1 vs player2
@VaingloryAI player1+player2+player3 vs player4+player5+player6
@VaingloryAI player1+player2+Lyra vs Lance+Joule+Adagio
VaingloryAI will reply back to the player with the predicted outcome and an image of how they were scored. 
If the bot receives a query for a player that we are unable to retreive data for, we will return an error message and remind them that Vainglory player names are case sensitive.
<p align="center">
  <img src="https://raw.githubusercontent.com/devfans/VaingloryAI/master/misc/AI_sample.jpg" alt="Sublime's custom image" width="800" />
</p>
Tweet Sample:
<p align="center">
  <img src="https://raw.githubusercontent.com/devfans/VaingloryAI/master/misc/Conversation.png" alt="Sublime's custom image" height="800"/>
</p>
# Design
The VaingloryAI selection of the winner is based on two components: Score Calcuations and a NeuralNet Prediction. When both are in agreement, we simply return the predicted result. When there is a disagreement we answer saying the player/hero score was lower but that our analysis puts them in the lead. 
## Score Calculations
For hero score calcuations we query all hero match data that we've downloaded into our own database. For players, we take their 10 most recent matches and make the calculation based on that data.  
Win Score: Average wins for the hero/player.
Kill Score: Average number of kills for this hero/player per match.
Death Score: Average number of deaths sustained by this hero/player per match.
Assist Score: Average number of assists made by this hero/player per match.
Farming Score: Average number of gold that this hero/player has farmed per match.
Overall Score: This is calculated by a formula that compiles all the results from the individual scores, each with a different weighting. Of course, the Death Score will have a negative Effect on the Overall Score, and the Win Score is calculated with a much higher weight than the Farming Score and Assist Score.
Weights for the calculations are as follows:
winsWeight = 1.8
killsWeight = 1
deathsWeight = -0.6
assistsWeight = 0.4
farmWeight = 0.3
levelWeight = 0.3
## NeuralNet Prediction
VaingloryAI uses also a neural network to make a prediction on the matchup query. The neural network has been trained with a huge chunk of match data mostly looking at players personal stats and heroes picked. A neural network with 6 layers is then used to compute the winner. The more data we are able to pull down the better we can train the neural network.
# Future Development
- Recognizing hero names in different languages and replaying back in the same language.
- Computing real Team's in Vainglory.
- Computing Guilds vs Guilds.
- Additional casual chat functionalities.
- Answers to other questions like what skills heroes have or what the hero rotation is this week.
# Setup
## Preparations
First, install pip packages for Tornado, Pillow and TwitterAPI
```
sudo pip install Tornado
sudo pip install Pillow
sudo pip install TwitterAPI
# For the Neural Network
sudo pip install http://download.pytorch.org/whl/cu75/torch-0.1.10.post2-cp27-none-linux_x86_64.whl 
sudo pip install torchvision
```
Next, register a Twitter account and create a Twitter application. When the Twitter application is ready, you will have the API token and your secret. You will also need to generate an access token with post permissions (for replying to players). Write these parameters in vaingloryai.conf after you make a clone of the repo.
## Neural network training (optional)
If you don't want to reuse our trained neural network or want to improve it, you need to do the following instructions. First of all, we advice you to use a computer with GPU compatible with CUDA 7.5 or 8.0 as it is stated on [pytorch website](http://pytorch.org/). Then run `python nn/trainer.py` to start the training process. Line 69: you can set the learning rate (`lr`) of the training process and line 88 you can change the loss target (representation of the difference with the expected outputs and the computed ones). The closest the loss value gets to zero the closest it will match the training set expected outputs. You can stop the training with a `Ctrl+C` the current state of the training will be saved then allowing you to resume the training afterwards. 
## Clone and Start
```
git clone https://github.com/devfans/VNG-Paul.git
cd VaingloryAI
./vaingloryai.py start
```
