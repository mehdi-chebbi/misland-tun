import psutil
import os
import time
from tabulate import tabulate
from common.models import MonitoringLog, MonitoringLogItem
from common.utils.settings_util import get_common_settings
import json
from django.utils import timezone
import schedule
import datetime
from django.conf import settings

GB_FACTOR = 1024**3

def format_flt(val):
    return "{:.2f}".format(flt(val))

def flt(val):
    return round(val, 2)

class CPUInfo:
    """
    Class to hold CPU Info
    """
    def __init__(self, initialize=False) -> None:
        self.physical_cores = 0
        self.total_cores = 0
        self.processor_speed = 0
        self.cpu_usage_per_core = 0
        self.total_cpu_usage = 0
        self.average_load = (0, 0, 0) #loadavg for 1, 5 and 15 minutes
        if initialize:
            self.get_info()

    def get_info(self):
        self.physical_cores = psutil.cpu_count(logical=False)
        self.total_cores = psutil.cpu_count(logical=True)
        self.processor_speed = ['Core {0}: {1}'.format(i, str(x.current)) for i, x in enumerate(psutil.cpu_freq(percpu=True))]
        self.cpu_usage_per_core = ['Core {0}: {1}%'.format(i, str(x)) for i, x in enumerate(psutil.cpu_percent(percpu=True, interval=1))]
        self.total_cpu_usage = flt(psutil.cpu_percent(interval=1))
        self.average_load = psutil.getloadavg() 

    def as_dict(self):
        return {
            "physical_cores": self.physical_cores,
            "total_cores": self.total_cores, 
            "processor_speed": self.processor_speed,
            "cpu_usage_per_core": self.cpu_usage_per_core, 
            "total_cpu_usage": self.total_cpu_usage
        }

    # @property
    # def cores(self):
    #     """
    #     Number of logical CPU cores 
    #     """
    #     return psutil.cpu_count()
    
    # @property
    # def utilization(self):
    #     """
    #     Percentage utilization 
    #     """
    #     return psutil.cpu_percent(interval=1)
    
    # @property
    # def load(self):
    #     """
    #     Get load over 1, 5 and 15 minutes 
    #     """
    #     # Getting loadover15 minutes
    #     load1, load5, load15 = psutil.getloadavg() 
    #     return load1, load5, load15
    
    # @property
    # def load_average(self):
    #     """
    #     Get load average over 15 minutes
    #     """
    #     # Getting loadover15 minutes
    #     load1, load5, load15 = psutil.getloadavg()
    #     cpu_usage = (load15/psutil.cpu_count()) * 100
    #     return cpu_usage
     
class MemoryInfo:
    """
    Class to hold Memory Info
    """
    def __init__(self, initialize=False) -> None: 
        self.total_memory = 0
        self.available_memory = 0
        self.used_memory = 0
        self.memory_utilization = 0
        if initialize:
            self.initialize()
        
    def initialize(self):
        info = psutil.virtual_memory()
        self.total_memory = flt(info.total / GB_FACTOR) #+ ' GB'
        self.available_memory = flt(info.available / GB_FACTOR) #+ ' GB'
        self.used_memory = flt(info.used / GB_FACTOR) #+ ' GB'
        self.memory_utilization = flt(info.percent) #+ "%"

    # info = psutil.virtual_memory()
    # # total_memory = info.total '0 GB'
    # # available_memory = '0 GB'
    # # used_memory = '0 GB'
    # # memory_utilization = '0 GB'

    # total_memory = flt(info.total / GB_FACTOR) + ' GB'
    # available_memory = flt(info.available / GB_FACTOR) + ' GB'
    # used_memory = flt(info.used / GB_FACTOR) + ' GB'
    # memory_utilization = flt(info.percent) + "%"

    # def __init__(self) -> None:
    #     self._memory = psutil.virtual_memory()

    # @property
    # def total(self):
    #     """
    #     Total memory in GB
    #     """
    #     return self._memory.total / GB_FACTOR
    
    # @property
    # def available(self):
    #     """
    #     Available memory in GB
    #     """
    #     return self._memory.available / GB_FACTOR
    
    # @property
    # def used(self):
    #     """
    #     Used memory in GB
    #     """
    #     return self._memory.used / GB_FACTOR
    
    # @property
    # def utilization(self):
    #     """
    #     Memory utilization as a %
    #     """
    #     return self._memory.percent
    
    def as_dict(self):
        """
        Retrieve all info as dict
        """
        return {
            "total_memory": self.total_memory,
            "available_memory": self.available_memory,
            "used_memory": self.used_memory,
            "memory_percentage": self.memory_utilization,
        }

class DiskInfoEntry:
    def __init__(self) -> None:
        self.mount_point = ''
        self.total_space = 0
        self.used_space = 0
        self.free_space = 0
        self.used_percentage = 0

class DiskInfo:
    """
    Class to hold disk info 
    """
    def __init__(self, initialize=False) -> None:
        self.entries = []
        if initialize:
            self.initialize()
        
    def initialize(self):
        partitions = psutil.disk_partitions(all=False)  
        for partition in partitions:
            if partition.mountpoint != '/':
                continue
            partition_usage = psutil.disk_usage(partition.mountpoint)
            entry = DiskInfoEntry()
            entry.mount_point = partition.mountpoint
            entry.total_space = partition_usage.total / GB_FACTOR
            entry.used_space = partition_usage.used / GB_FACTOR
            entry.free_space = partition_usage.free / GB_FACTOR
            entry.used_percentage = partition_usage.percent
            self.entries.append(entry)

            # disk_info[partition.mountpoint] =  {
            #     "total_space": flt(partition_usage.total / GB_FACTOR) + ' GB',
            #     "used_space": flt(partition_usage.used / GB_FACTOR) + ' GB',
            #     "free_space": flt(partition_usage.free / GB_FACTOR) + ' GB',
            #     "used_percentage": flt(partition_usage.percent) + "%"
            # } 
    
    def as_dict(self):
        disk_info = {}
        for entry in self.entries:
            disk_info[entry.mount_point] = {
                "total_space": format_flt(entry.total_space) + ' GB',
                "used_space": format_flt(entry.used_space) + ' GB',
                "free_space": format_flt(entry.free_space) + ' GB',
                "used_percentage": format_flt(entry.used_percentage) + "%"
            }
        return disk_info

    # def __init__(self, path='/') -> None:
    #     self._disk = psutil.disk_usage(path=path)
        
    # @property
    # def total(self):
    #     """
    #     Total disk in GB
    #     """
    #     return self._disk.total / GB_FACTOR
    
    # @property
    # def used(self):
    #     """
    #     USed disk in GB
    #     """
    #     return self._disk.used / GB_FACTOR
    
    # @property
    # def utilization(self):
    #     """
    #     Disk in %
    #     """
    #     return self._disk.percent
    
class HeatInfoEntry:

    def __init__(self, label, current, high, critical) -> int:
        self._label = label
        self._current = current
        self._high = high
        self._critical = critical
        
    @property
    def label(self):
        """
        Label for the sensor 
        """
        return self._label

    @property
    def current(self):
        """
        Current temp
        """
        return self._current
    
    # @property.setter
    # def current(self, value):
    #     self._current = value

    @property
    def high(self):
        """
        Highest temp
        """
        return self._high
    
    # @property.setter
    # def high(self, value):
    #     self._high = value

    @property
    def critical(self):
        """
        Critical temp
        """
        return self._critical
    
    # @property.setter
    # def high(self, value):
    #     self._critical = value

class HeatInfo:
    """
    Class to hold Heat info 
    """
    def __init__(self) -> None:
        self._temperatures = psutil.sensors_temperatures()

    @property
    def temperatures(self):
        res = []
        if 'coretemp' in self._temperatures:
            for entry in self._temperatures['coretemp']:
                res.append(HeatInfoEntry(label=entry.label, current=entry.current, high=entry.high, critical=entry.critical))
        return res

class TimeInfo:
    def __init__(self) -> None:
        self.boot_time = psutil.boot_time()
        self.current_time = time.time()
        self.uptime_seconds = self.current_time - self.boot_time
        self.uptime_minutes = self.uptime_seconds // 60
        self.uptime_hours = self.uptime_minutes // 60
        self.uptime_days = self.uptime_hours // 24
        self.uptime_str = "{} days, {} hours, {} minutes, {} seconds".format(int(self.uptime_days), 
                                                                             int(self.uptime_hours % 24), 
                                                                             int(self.uptime_minutes % 60), 
                                                                             int(self.uptime_seconds % 60))
    def as_dict(self):
        return {
            'boot_time': self.boot_time,
            'current_time': self.current_time,
            'uptime_seconds': self.uptime_seconds,
            'uptime_minutes': self.uptime_minutes,
            'uptime_hours': self.uptime_hours,
            'uptime_days': self.uptime_days,
            'uptime_str': self.uptime_str,
        }

class MonitoringUtil2:
    #@staticmethod
    def cpu_info():
        """
        Get CPU info 
        """
        return CPUInfo()

    def memory_info():
        """
        Get Memory info 
        """
        return MemoryInfo()

    def disk_info(path='/'):
        """
        Get Disk info 
        """
        return DiskInfo(path=path)

    def heat_info():
        """
        Get heat info 
        """
        return HeatInfo()
    
    @staticmethod
    def tabulate_as_str():
        """
        Return monitoring readings as a table
        """
        def _append_list(vals, headers, is_repeating_entry=0):
            if not is_repeating_entry:
                dict_vals[0].update(dict(zip(headers, vals)))
            else:
                dict_vals.append(dict(zip(headers, vals)))
            # for i, val in enumerate(vals):
            #     list_vals[0].append(val)
            #     list_headers.append(headers[i])

        cpu = MonitoringUtil.cpu_info()
        memory = MonitoringUtil.memory_info()
        disk = MonitoringUtil.disk_info()
        heat = MonitoringUtil.heat_info()
        list_vals = [[]]
        list_headers = []
        dict_vals = [{}]

        _append_list(vals=[cpu.cores, cpu.utilization], headers=['Cores', 'CPU Utilization (%)'])
        _append_list(vals=[memory.total, memory.available, memory.utilization], headers=['Total RAM (GB)', 'Available RAM (GB)', 'RAM Utilization (%)'])
        _append_list(vals=[disk.total, disk.used, disk.utilization], headers=['Total Disk (GB)', 'Disk Used (GB)', 'Disk Utilization (%)'])
        for i, entry in enumerate(heat.temperatures):
            if i == 0:
                _append_list(vals=[entry.label, entry.current, entry.high, entry.critical], 
                             headers=['Sensor', 'Temp current', 'Temp high', 'Temp critical'])
            else:
                _append_list(vals=[entry.label, entry.current, entry.high, entry.critical], 
                             headers=['Sensor', 'Temp current', 'Temp high', 'Temp critical'], 
                             is_repeating_entry=True)

        print("List vals:", list_vals)
        print("List headers:", list_headers)
        print("Dict vals: ", dict_vals) 
        #return tabulate(list_vals, list_headers, tablefmt="grid")
        return tabulate(dict_vals, headers='keys', tablefmt="html")

class ResourceDelta:
    """
    Model to log resource delta changes
    """ 
    def __init__(self) -> None:
        self.memory_usage_array = []
        self.cpu_usage_array = []
        self.disk_usage_array = []

    def as_dict(self):
        return {
            "memory_usage_array": self.memory_usage_array,
            "cpu_usage_array": self.cpu_usage_array,
            "disk_usage_array": self.disk_usage_array
        }


class MonitoringUtil:
    def kernel_info(self):
        info = os.uname()
        return {
            "kernel_version": info.release,
            "system_name": info.sysname,
            "node_name": info.nodename,
            "machine": info.machine
        }

    def memory_info(self, as_dict=True):
        info = MemoryInfo(initialize=True)
        return info.as_dict() if as_dict else info
        # info = psutil.virtual_memory()
        # return {
        #     "total_memory": flt(info.total / GB_FACTOR) + ' GB',
        #     "available_memory": flt(info.available / GB_FACTOR) + ' GB',
        #     "used_memory": flt(info.used / GB_FACTOR) + ' GB',
        #     "memory_utilization": flt(info.percent) + "%"
        # }
 
    def cpu_info(self, as_dict=True):
        info = CPUInfo(initialize=True)
        return info.as_dict() if as_dict else info
        # return {
        #     "physical_cores": psutil.cpu_count(logical=False),
        #     "total_cores": psutil.cpu_count(logical=True),
        #     "processor_speed": ['Core {0}: {1}'.format(i, str(x.current)) for i, x in enumerate(psutil.cpu_freq(percpu=True))],
        #     "cpu_usage_per_core": ['Core {0}: {1}%'.format(i, str(x)) for i, x in enumerate(psutil.cpu_percent(percpu=True, interval=1))],
        #     "total_cpu_usage": flt(psutil.cpu_percent(interval=1)) + "%"
        # }
     
    def disk_info(self, as_dict=True):
        info = DiskInfo(initialize=True)
        return info.as_dict() if as_dict else info
        # partitions = psutil.disk_partitions(all=False) 
        # disk_info = {}
        # for partition in partitions:
        #     if partition.mountpoint != '/':
        #         continue
        #     partition_usage = psutil.disk_usage(partition.mountpoint)
        #     disk_info[partition.mountpoint] = {
        #         "total_space": flt(partition_usage.total / GB_FACTOR) + ' GB',
        #         "used_space": flt(partition_usage.used / GB_FACTOR) + ' GB',
        #         "free_space": flt(partition_usage.free / GB_FACTOR) + ' GB',
        #         "used_percentage": flt(partition_usage.percent) + "%"
        #     }
        # return disk_info

    def heat_info(self):
        info = HeatInfo().temperatures
        return info
     
    def network_info(self):
        net_io_counters = psutil.net_io_counters()
        return {
            "bytes_sent": net_io_counters.bytes_sent,
            "bytes_recv": net_io_counters.bytes_recv
        }
     
    def process_info(self):
        process_info = []
        for process in psutil.process_iter(["pid", "name", "memory_percent", "cpu_percent"]):
            try:
                if process.info['memory_percent'] and process.info['cpu_percent']:
                    process_info.append({
                        "pid": process.info['pid'],
                        "name": process.info['name'],
                        "memory_percent": process.info['memory_percent'],
                        "cpu_percent": format_flt(process.info['cpu_percent']) + "%"
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return process_info
        
    def load_average(self):
        load_avg_1, load_avg_5, load_avg_15 = psutil.getloadavg()
        return {
            "load_average_1": format_flt(load_avg_1),
            "load_average_5": format_flt(load_avg_5),
            "load_average_15": format_flt(load_avg_15)
        }
     
    def disk_io_counters(self):
        io_counters = psutil.disk_io_counters()
        return {
            "read_count": io_counters.read_count,
            "write_count": io_counters.write_count,
            "read_bytes": io_counters.read_bytes,
            "write_bytes": io_counters.write_bytes,
            "read_time": io_counters.read_time,
            "write_time": io_counters.write_time
        }
 
    def net_io_counters(self):
        io_counters = psutil.net_io_counters()
        return {
            "bytes_sent": io_counters.bytes_sent,
            "bytes_recv": io_counters.bytes_recv,
            "packets_sent": io_counters.packets_sent,
            "packets_recv": io_counters.packets_recv,
            "errin": io_counters.errin,
            "errout": io_counters.errout,
            "dropin": io_counters.dropin,
            "dropout": io_counters.dropout
        }
    
    def system_uptime(self, as_dict=True):
        info = TimeInfo()
        return info.as_dict() if as_dict else info
        # boot_time = psutil.boot_time()
        # current_time = time.time()
        # uptime_seconds = current_time - boot_time
        # uptime_minutes = uptime_seconds // 60
        # uptime_hours = uptime_minutes // 60
        # uptime_days = uptime_hours // 24
        # uptime_str = "{} days, {} hours, {} minutes, {} seconds".format(int(uptime_days), int(uptime_hours % 24), int(uptime_minutes % 60), int(uptime_seconds % 60))
        # return {
        #     "uptime": uptime_str
        # }
    
    @staticmethod
    def as_dict():
        """
        Get monitoring info as dict
        """
        cls = MonitoringUtil()
        return {
            "kernel_info": cls.kernel_info(),
            "memory_info": cls.memory_info(),
            "cpu_info": cls.cpu_info(),
            "disk_info": cls.disk_info(),
            "network_info": cls.network_info(),
            "process_info": cls.process_info(),
            "system_uptime": cls.system_uptime(),
            "load_average": cls.load_average(),
            "disk_io_counters": cls.disk_io_counters(),
            "net_io_counters": cls.net_io_counters()
        }
    
# res = MonitoringUtil.as_dict()
# import pprint
# pprint.pprint(res)
# print(res)

def truncate_mem_profile():
    try:        
        # if os.path.exists(settings.MEMORY_PROFILER_LOG_FILE):
        #     os.remove(settings.MEMORY_PROFILER_LOG_FILE)
        # # create it after deleting
        fp = open(settings.MEMORY_PROFILER_LOG_FILE, 'w+') 
        fp.write('')
    except:
        pass

def start_monitoring(execution_name, params, caller_id, caller_type, caller_details):
    """
    Start monitoring
    """  
    setts = get_common_settings()
    if not setts.enable_execution_monitoring:
        return None
 
    time_info = MonitoringUtil().system_uptime(as_dict=False)
    doc = MonitoringLog.objects.create(
        execution_name=execution_name,
        params=json.dumps(params),
        caller_id=caller_id,
        caller_type=caller_type,
        caller_details=caller_details,
        # resource_delta_stats={},
        post_execution_stats={},
        boot_time=datetime.datetime.fromtimestamp(time_info.boot_time),
        uptime_minutes=time_info.uptime_minutes,
        pre_execution_stats=MonitoringUtil.as_dict()
    )
    # Monitor resources from a separate thread
    import threading
    t = threading.Thread(target=monitor_resources, args=(doc.id,), kwargs={})
    t.setDaemon(True) 
    t.start()
    return doc

def monitor_resources(monitoring_log_id):
    def _update_stats(doc):
        # stats = doc.resource_delta_stats or {'cpu_usage_array':[], 'disk_usage_array': [], 'memory_usage_array': []}
        stats = {'cpu_usage_array':[], 'disk_usage_array': [], 'memory_usage_array': []}
        delta = ResourceDelta()
        # initialize with existing values first
        delta.cpu_usage_array = stats['cpu_usage_array']
        delta.disk_usage_array = stats['disk_usage_array']
        delta.memory_usage_array = stats['memory_usage_array']

        util = MonitoringUtil()
        memory = util.memory_info(as_dict=False)
        cpu = util.cpu_info(as_dict=False)
        disk_info = util.disk_info(as_dict=False)
        heat_info = MonitoringUtil().heat_info()

        time_key = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        delta.memory_usage_array.append([time_key, memory.memory_utilization])
        delta.cpu_usage_array.append([time_key, cpu.total_cpu_usage])
        delta.disk_usage_array.append([time_key, [[x.mount_point, format_flt(x.used_space) + 'GB'] for x in disk_info.entries]])

        # doc.resource_delta_stats = delta.as_dict()
        # doc.save()
        time_key = timezone.now()
        d = MonitoringLogItem.objects.create(
            time_entry=time_key,
            monitoring_log=doc,
            cpu=cpu.total_cpu_usage,
            memory=memory.memory_utilization,
            disk=str([[x.mount_point, flt(x.used_space)] for x in disk_info.entries]),
            highest_temp=max([x.current for x in heat_info])
        )
        d.save()

        critical = False
        # check if critical levels are reached
        if memory.memory_utilization >= 90:
            doc.is_critical_memory_usage = True
            critical = True
        if cpu.total_cpu_usage >= 90:
            doc.is_critical_cpu_usage = True
            critical = True
        high_temps = [x for x in heat_info if x.current >= x.critical]
        if high_temps:
            doc.is_critical_temp = True
            critical = True
        if critical:
            doc.save() 

    def _log_resource_utilization():
        """
        Check if the scheduled task has completed. If yes, exit the scheduling
        """
        print("Other thread")
        doc = MonitoringLog.objects.get(id=monitoring_log_id)
        if doc:
            _update_stats(doc)
        else:
            # if no doc, exit task
            return schedule.CancelJob
        if doc.is_completed:
            # If computation has completed, no need to update the stats, just exit
            # _update_stats(doc)
            return schedule.CancelJob
    
    schedule.every(2).seconds.do(_log_resource_utilization)
    while True:
        schedule.run_pending()
        time.sleep(1)

def stop_monitoring(monitoring_log_id):
    def get_mem_profile():
        fp = open(settings.MEMORY_PROFILER_LOG_FILE, 'r')
        return fp.read()
 
    setts = get_common_settings()
    if not setts.enable_execution_monitoring:
        return None
    doc = MonitoringLog.objects.get(id=monitoring_log_id)
    doc.execution_end_time = timezone.now()
    doc.post_execution_stats = MonitoringUtil.as_dict() #json.dumps(MonitoringUtil.as_dict())
    # doc.resource_delta_stats = {}
    doc.mem_profile = get_mem_profile()
    doc.is_completed = True
    doc.save()
    time.sleep(2)
    truncate_mem_profile()
   