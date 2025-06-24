# specter
## Description:
specter is a bot that plays Clash of Clans. It's main feature is its attacking capabilities, allowing you fill up your storages while staying within a desired trophy range, as well as trophy push, all on its own. This project was inspired by the removal of troop training times, with the goal of seeing how far I can take a brand new account over the course of the summer (and maybe beyond).

I am using iPhone Mirroring on a Mac for an "emulator". With a few tweaks, it should work no problem on Bluestacks or other popular emulators, on any OS.

## Featured attack strategies:
### Balloons:
For town halls 4-6. This strategy can place lightning spells on detected air defenses, followed by deploying balloons in bursts on the border region closest to the highest level air defense.

### Dragons:
For town halls 7-8. For trophy pushing, this strategy places lightning spells on the highest level air defense, taking it out. It then places dragons in pairs on the border region furthest from the destroyed air defense. Most bases are symmetrical, meaning that the dragons should be closer to the remaining air defenses. The hero is then placed at random anywhere on the border. For loot farming, this strategy (will soon) follow the same strategy, except it will place the dragons individually and on both sides of the base. The idea is that dead bases have most of their loot in collectors, mines, and drills on the outsides of the base, so spreading the dragons out more should help to retrieve the most loot.

### (soon) Lavaloons:
For town halls 9-10. This strategy will attack from the side of the base with the highest level air defense and perform a traditional lavaloon attack.

### (soon) Edrags:
For town halls 11-?. Traditional edrag attack.

## Breakdown of files:
main.py - main loop
attack.py - everything pertaining to attacking
specter.py - text scanning, image processing, fetching current state
vars.py - global variables
archive.py - functions no longer in use
idle.py - prevents timing out in game
train.py - train model
predict.py - predict using model
blah.py - random test code

## Install all necessary packages:
pip install -r requirements.txt

## Future plans:
- Better error handling (client out of sync, iPhone Mirroring disconnection)
- Better text scanning for trophies, loot, etc.
