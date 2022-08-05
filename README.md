# Redis Compatible Bloom Filter

Attempt to build a Bloom Filter implementation using a Pimoroni Unicorn Hat on a Raspberry Pi that talks the RESP protocol.  This is the repo to support my livestream series [on Twitch](https://twitch.tv/redisinc).

The current state of this is that it has basic support for `SADD`, `SISMEMBER` and `SCARD` commands with little error checking.

It uses `nodemon` to restart the process when you save changes, so you'll need both Python 3 and Node.js.

Setup / install dependencies:

```bash
npm install
python3 -m venv venv
. ./venv/bin/activate
```

Start server on port 6379 (turn off any running Redis instance first):

```bash
./run.sh
```

Example interactions using the real `redis-cli`:

```
127.0.0.1:6379> sadd myset a b c
(integer) 3
127.0.0.1:6379> sadd myset a b d e
(integer) 2
127.0.0.1:6379> sismember myset r
(integer) 0
127.0.0.1:6379> sismember myset d
(integer) 1
127.0.0.1:6379> scard myset
(integer) 5
```