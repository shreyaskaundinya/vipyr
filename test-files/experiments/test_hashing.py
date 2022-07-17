from hashlib import sha256, sha512, blake2b, blake2s
from zlib import crc32
from json import dumps
from datetime import datetime


el = {
    "key": "akghakghadkg",
    "type": "div",
    "props": {
        "style": "akghakgadhdakghadlkgahngadkhda;lgdkahgd",
        "date": "kdhakga",
        "time": "kahjglkdahgakdgh",
        "color": "ksdgaklgakgahgkahgakd"
    }
}

print(dumps(el))

TEST_RUNS = 100
ITER_RUNS = 100000

def timeit(func, title):
    delta = 0
    start = datetime.now()
    func()
    end = datetime.now()
    print(title, " took => ", end-start)

def test_sha256():
    for i in range(0, ITER_RUNS):
        h = sha256(dumps(el).encode()).hexdigest()
    print(h)

def test_sha512():
    for i in range(0, ITER_RUNS):
        h = sha512(dumps(el).encode()).hexdigest()
    print(h)

def test_hash():
    for i in range(0, ITER_RUNS):
        h = hash(dumps(el))
    print(h)

def test_blake2b():
    for i in range(0, ITER_RUNS):
        h = blake2b(dumps(el).encode()).hexdigest()
    print(h)

def test_blake2s():
    for i in range(0, ITER_RUNS):
        h = blake2s(dumps(el).encode()).hexdigest()
    print(h)

def test_crc32():
    for i in range(0, ITER_RUNS):
        h = crc32(dumps(el).encode())
    print(h)

timeit(test_sha256, "sha256")
timeit(test_sha512, "sha512")
timeit(test_hash, "hash")
timeit(test_blake2b, "blake2b")
timeit(test_blake2s, "blake2s")
timeit(test_crc32, "Cyclic redunduncy")

