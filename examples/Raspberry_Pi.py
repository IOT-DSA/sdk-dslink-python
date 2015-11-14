import psutil
import subprocess

from dslink.DSLink import DSLink, Configuration, Node
from twisted.internet import reactor


class RaspberryPiDSLink(DSLink):
    def __init__(self):
        self.cpu_temp = None
        self.cpu_usage = None
        self.mem_avail = None
        self.mem_total = None
        self.mem_used = None

        DSLink.__init__(self, Configuration("raspberry-pi", responder=True, no_save_nodes=True))

        self.update_data()

    def get_default_nodes(self):
        root = self.get_root_node()

        self.cpu_usage = Node("cpu_usage", root)
        self.cpu_usage.set_name("CPU Usage")
        self.cpu_usage.set_type("number")
        self.cpu_usage.set_value(0.0)
        root.add_child(self.cpu_usage)

        self.cpu_temp = Node("cpu_temp", root)
        self.cpu_temp.set_name("CPU Temperature")
        self.cpu_temp.set_type("number")
        self.cpu_temp.set_value(0.0)
        root.add_child(self.cpu_temp)

        self.mem_avail = Node("mem_avail", root)
        self.mem_avail.set_name("Memory Available")
        self.mem_avail.set_type("int")
        self.mem_avail.set_value(0)
        root.add_child(self.mem_avail)

        self.mem_total = Node("mem_total", root)
        self.mem_total.set_name("Memory Total")
        self.mem_total.set_type("int")
        self.mem_total.set_value(0)
        root.add_child(self.mem_total)

        self.mem_used = Node("mem_used", root)
        self.mem_used.set_name("Memory Used")
        self.mem_used.set_type("int")
        self.mem_used.set_value(0)
        root.add_child(self.mem_used)

        return root

    def update_data(self):
        self.cpu_usage.set_value(psutil.cpu_percent())
        self.cpu_temp.set_value(self.get_temperature())
        meminfo = psutil.virtual_memory()
        self.mem_avail.set_value(meminfo.available)
        self.mem_total.set_value(meminfo.total)
        self.mem_used.set_value(meminfo.used)
        reactor.callLater(1, self.update_data)

    @staticmethod
    def get_temperature():
        try:
            s = subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_temp"])
            return float(s.split('=')[1][:-3])
        except:
            return 0.0

if __name__ == "__main__":
    RaspberryPiDSLink()
