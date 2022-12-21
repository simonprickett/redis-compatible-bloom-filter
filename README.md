# Redis Compatible Bloom Filter

Attempt to build a Bloom Filter implementation using a [Pimoroni Unicorn HAT](https://shop.pimoroni.com/products/unicorn-hat?variant=932565325) on a Raspberry Pi that talks the RESP protocol.  This is the repo to support my livestream series "Things on Thursdays" ([see all episodes](https://simonprickett.dev/things-on-thursdays-livestreams/)).  This needs to be run on a Raspberry Pi with a Unicorn HAT attached.

Here's the videos from this series:

* [Episode One - RESP protocol and exploring Redis Sets](https://www.youtube.com/watch?v=uyjAFP73ttI)
* [Episode Two - Working with the LEDs and Bloom Filter Commands](https://www.youtube.com/watch?v=Ym4g5iti3bo)

The current state of this is that it has basic support for `BF.ADD`, `BF.EXISTS` and `BF.MADD` commands with little error checking.

It uses `nodemon` to restart the process when you save changes, so you'll need both Python 3 and Node.js if you want to take advantage of that.

Setup / install dependencies:

```bash
npm install
python3 -m venv venv
. ./venv/bin/activate
```

Start server on port 6379 (turn off any running Redis instance first):

```bash
sudo bash
./run.sh
```

Or without `nodemon`:

```bash
sudo bash
python redis-server.py
```

Note that you need to run as `root` because of the way that the Unicorn Hat LED SDK works.

Example interactions using the real `redis-cli`:

```
192.168.4.39:6379> bf.madd leds a b c
1) (integer) 1
2) (integer) 1
3) (integer) 1
(14.64s)
192.168.4.39:6379> bf.madd leds a b d e
1) (integer) 0
2) (integer) 0
3) (integer) 1
4) (integer) 1
(29.20s)
192.168.4.39:6379> bf.exists leds r
(integer) 0
(2.45s)
192.168.4.39:6379> bf.exists leds d
(integer) 1
(7.31s)
```

Note that the key name isn't used in the code as there's only one Unicorn HAT attached to the Pi.
