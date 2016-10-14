import argparse
import consul
import datetime
import etcd
import json
import random
import string
import sys
import threading
import time

parser = argparse.ArgumentParser(
    description='Run benchmark k/v test')

parser.add_argument("--depth", dest="depth", help="How deep to go for the test", type=int, default=3)
parser.add_argument("--width", dest="width", help="How wide should each level be", type=int, default=30)
parser.add_argument("--keysize", dest="keysize", help="How many characters should each key contain", type=int, default=5)
parser.add_argument("--valuesize", dest="valuesize", help="How many characters should each value contain", type=int, default=25)
parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity", default=False)
subparsers = parser.add_subparsers(dest="target", help='Target KV stores')
consul_parser = subparsers.add_parser('consul', help='run against consul')
consul_parser.add_argument("--host", dest="host", help="Target host", default='192.168.33.60')
consul_parser.add_argument("--port", dest="port", help="Target port", type=int, default=8500)
etcd_parser = subparsers.add_parser('etcd', help='run against etcd')
etcd_parser.add_argument("--host", dest="host", help="Target host", default='192.168.33.50')
etcd_parser.add_argument("--port", dest="port", help="Target port", type=int, default=4001)

args = parser.parse_args()

class main(object):
    def __init__(self, args):
        self.debug = args.debug
        self.base_key = "benchmark" # all our keys should live in one space for easy cleanup
        self.depth = args.depth
        self.width = args.width
        self.keysize = args.keysize
        self.valuesize = args.valuesize
        self.key_count = 0 # how many total keys we have 
        self.data = {self.base_key: self.gendata(args.depth, args.width)}
        self.run_load = False
        self.load_rate = {}
        
    
    def printSourceData(self):
        print json.dumps(self.data, indent=2)
        print "Depth: %i" % self.depth
        print "Width: %i" % self.width
        print "Keys: %i" % self.key_count
        print "Values: %i" % self.leaves 
        
    def gendata(self, depth, width):
        data = {}
        if depth == 1:
            for i in range(width):
                self.key_count += 1
                data[self.genstring(self.keysize)] = self.genstring(self.valuesize)
        else:
            for i in range(width):
                self.key_count += 1
                data[self.genstring(self.keysize)] = self.gendata(depth - 1, width)
        return data
    
    def genstring(self, size):
        key = []
        for i in range(size):
            key.append(random.choice(string.letters))
        return "".join(key)
    
    def getValueFromSourceKey(self, key):
        if isinstance(key, str):
            keys = key.split("/")
            if keys[0] == "":
                keys.pop(0)
        data = self.data
        for k in keys:
            if not isinstance(data[k], dict):
                return data[k]
            else:
                data = data[k]
            
        
    def getRandomKey(self, depth=None):
        def get_key(keys, mydict, depth):
            if depth == 0:
                return keys
            else:
                newkey = random.choice(mydict.keys())
                keys.append(newkey)
                return get_key(keys, mydict[newkey], depth - 1)
            
        if depth == None:
            depth = self.depth
        return self.makeKey([self.base_key] + get_key([], self.data[self.base_key], depth))
             
    @property
    def leaves(self):
        leaf_keys = []
        def traverse(keys, mydict, depth):
            if depth == 0:
                for key in mydict.keys():
                    leaf_keys.append(self.makeKey(keys + [key]))
            else:
                for key in mydict.keys():
                    traverse(keys + [key], mydict[key], depth - 1)
        traverse([], self.data, self.depth)
        return leaf_keys
    
    def makeKey(self, keys):
        raise NotImplementedError
    
    def startLoad(self, duration = None):
        def load(end_time):
            self.run_load = True
            self.load_count = 0
            while self.run_load and datetime.datetime.now() < end_time:
                for leaf in self.leaves:
                    if self.debug:
                        print "Writing: %s" % leaf
                    self.write(leaf, self.getValueFromSourceKey(leaf))
                    self.load_count += 1
                    if not self.run_load or datetime.datetime.now() >= end_time:
                        self.run_load = False
                        if self.debug:
                            print "End load"
                        return
            self.run_load = False
            if self.debug:
                print "End load"
            return
        def collect_metrics(load_thread, interval = 10):
            start_time = datetime.datetime.now()
            while load_thread.isAlive():
                elapsed_time = int((datetime.datetime.now() - start_time).total_seconds())
                if elapsed_time > 0 and elapsed_time % interval == 0:
                    curcount = self.load_count
                    self.load_count = 0
                    print "Elapsed Time: %i\tRate: %i/second " % (elapsed_time, curcount / interval)
                    self.load_rate[elapsed_time] = int(curcount / interval)
                time.sleep(1)
                  
                    
        if isinstance(duration, int):
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
        else:
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=300)
        if not self.run_load:
            load_thread = threading.Thread(target=load, kwargs={"end_time": end_time}, name="LoadThread")
            load_thread.start()
            metrics_thread = threading.Thread(target=collect_metrics, kwargs={"load_thread": load_thread}, name="MetricsThread")
            metrics_thread.start()
    
    def stopLoad(self):
        self.run_load = False
        
class consulTest(main):
    def __init__(self, args):
        self.client = consul.Consul(host=args.host, port=args.port)
        super(consulTest, self).__init__(args)
    
    def deleteAll(self):
        if self.client.kv.get(self.base_key)[1] != None:
            self.client.kv.delete(self.base_key, recurse=True)

    def makeKey(self, keys):
        return "/".join(keys)
    
    def read(self, key):
        if isinstance(key, list):
            key = self.makeKey(key)
        return self.client.kv.get(key)[1]
    
    def write(self, key, value):
        if isinstance(key, list):
            key = self.makeKey(key)
        start_time = datetime.datetime.now()
        self.client.kv.put(key, value)
        return (datetime.datetime.now() - start_time).microseconds
            
        
class etcdTest(main):
    def __init__(self, args):
        self.client = etcd.Client(host=args.host, port=args.port)
        super(etcdTest, self).__init__(args)
    
    def makeKey(self, keys):
        ret = "/".join(keys)
        if ret[0] != "/":
            return "/%s" % ret
        return ret
    
    def printClusterData(self):
        children = []
        for child in self.client.read(self.makeKey([self.base_key]), recursive=True).children:
            children.append(child.key)
        for key in sorted(children):
            print "%s: %s" % (key, self.client.read(key).value)
            
    def write(self, key, value):
        start_time = datetime.datetime.now()
        self.client.write(key, value)
        end_time = datetime.datetime.now()
        return (end_time - start_time).microseconds
        
    def deleteAll(self):
        try:
            self.client.read(self.makeKey([self.base_key]))
            self.client.delete(self.makeKey([self.base_key]), recursive=True)
        except etcd.EtcdKeyNotFound:
            pass
    def read(self, key):
        if isinstance(key, list):
            key = self.makeKey(key)
        ret = self.client.read(key)
        return ret.value

if args.target == "etcd":
    cl = etcdTest(args)
elif args.target == "consul":
    cl = consulTest(args)
else:
    print "KV store %s is not supported by this tool." % args.target
    sys.exit(1)
print "Keys: %i" % cl.key_count
for i in range(3):
    try:
        cl.deleteAll()
        cl.startLoad()
        time.sleep(60)
        cl.stopLoad()
    except KeyboardInterrupt:
        cl.stopLoad()
        raise
    
