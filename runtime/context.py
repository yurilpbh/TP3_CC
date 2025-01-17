import os
import datetime
import redis

class Context(object):
    
    """
    Context Object
    """
    host = None
    port = None
    input_key = None
    output_key = None
    last_execution = None
    env = None
    monitoring_interval = 5
    
    def __init__(self, host='localhost', port=6379, input_key=None, output_key=None):
        self.host = host
        self.port = port
        self.input_key = input_key
        self.output_key = output_key
        tmp = os.path.getmtime("/runtime/usermodule.py")
        self.function_getmtime = datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')
        self.last_execution = None
        self.r_server = redis.Redis(host=host, port=port, charset="utf-8", decode_responses=True)
        self.env = {}

    def confirm_execution(self):
        self.last_execution = datetime.datetime.now()

    def set_env(self, new):
        self.env = new

    def set_input_key(self, input_key):
        self.input_key = input_key
        
    def set_interval(self, monitoring_interval):
        print(self.monitoring_interval)
        print(monitoring_interval)
        self.monitoring_interval = monitoring_interval
        print(self.monitoring_interval)
        
    def get_data(self):
        return self.r_server.get(self.input_key)
        
    def set_data(self, data):
        self.r_server.set(self.output_key, data)
    
    @staticmethod
    def help():
        print("""
        :param host: Address running Redis server
        :param port: Port running Redis server
        :param input_key: input key of Redis
        :param output_key: output key to store data in Redis
        :param function_getmtime: Timestamp of last update in usermodule file
        :param last_execution: Timestamp of last confirmed execution (and store)
        :param env: Dictionary to be used as context
        :param monitoring_interval: Time to wait before execute handler again
        """)
