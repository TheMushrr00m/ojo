![Ojo Icon 128x128](http://i.imgur.com/C8RZmp2.png)

# Ojo - a fast and pretty image viewer. [pronounced 'oho']

## Ojo's goals:

1. Ojo's general goal is to become the best image viewer for photography-related work on Linux. To serve as the first step in organizing images.
2. It should start and show a single image as fast as possible - 90% of the time this is all that an image viewer is used for [it does now, need to keep it this way]
3. It should look great and be very unobstrusive when viewing images, so as not to distract from the main content
4. It should support RAW - this is lacking in most other images viewers. [it does now, for viewing, no export options]
5. It should be easy to quickly zoom-in to 100% to a certain part of the image. [we have zooming to 100% now and fit-to-window, but no other-finer grain zooming options]
6. It should provide some simple but convenient Trash, Copy and Move functionality. [nothing of these yet]

## Tech stack
Ojo is based on these technologies: Python, GTK and HTML/JS/CSS with jQuery in an embedded WebKit

## Installation
To install on Ubuntu, Mint or other Ubuntu derivatives:
```
sudo add-apt-repository -y ppa:ojo/daily
sudo apt-get update
sudo apt-get install ojo
```

## Run from code and contribute
1. First install ojo from the PPA above, this would pull all necessary dependencies. Alternatively, manually install the dependencies listed in [debian/control](debian/control).
2. Clone repo
3. Run [bin/ojo](bin/ojo), ojo should start.
4. Hack away, and open a pull-request when ready, or better - immediately once you decide what you want do. For new features, please sync with me before you start - peterlevi AT peterlevi.com. 

## Keyboard shortcuts
```
Enter - toggles between single image / browse mode
F11 - toggles fullscreen (also F when viewing a single image)
[image mode] Arrows and PgUp/PgDown - move back and forth between images
[browse mode] Arrows and PgUp/PgDown - navigate around
[image mode] Press and hold mouse to zoom to specific point at 100%, then hold and move to "look around"
[image mode] Z to toggle zoom between 100% and Fit-to-window
[browse mode] Enter letters directly to quick-filter the images by filename
[browse mode] Backspace moves up, Enter selects currently active link
```

## Screenshots
Single image view:
![Ojo - Single image view](http://i.imgur.com/oa1Dr2I.png)

Press Enter to enter Browse mode:
![Ojo - Browse mode](http://i.imgur.com/fUcbhMY.png)

Ojo in the Dash:
![Ojo in the Dash](http://i.imgur.com/WJZpEkZ.png)


