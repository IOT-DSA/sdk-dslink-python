import psutil
import subprocess

from dslink.DSLink import DSLink, Configuration, Node
from twisted.internet import reactor


class RaspberryPiDSLink(DSLink):
    def start(self):

        self.cpu_usage = self.super_root.get("/cpu_usage")
        self.cpu_temp = self.super_root.get("/cpu_temp")
        self.mem_avail = self.super_root.get("/mem_avail")
        self.mem_total = self.super_root.get("/mem_total")
        self.mem_used = self.super_root.get("/mem_used")

        self.update_data()

    def get_default_nodes(self):
        root = self.get_root_node()

        cpu_usage = Node("cpu_usage", root)
        cpu_usage.set_name("CPU Usage")
        cpu_usage.set_type("number")
        cpu_usage.set_value(0.0)
        root.add_child(cpu_usage)

        cpu_temp = Node("cpu_temp", root)
        cpu_temp.set_name("CPU Temperature")
        cpu_temp.set_type("number")
        cpu_temp.set_value(0.0)
        root.add_child(cpu_temp)

        mem_avail = Node("mem_avail", root)
        mem_avail.set_name("Memory Available")
        mem_avail.set_type("int")
        mem_avail.set_value(0)
        root.add_child(mem_avail)

        mem_total = Node("mem_total", root)
        mem_total.set_name("Memory Total")
        mem_total.set_type("int")
        mem_total.set_value(0)
        root.add_child(mem_total)

        mem_used = Node("mem_used", root)
        mem_used.set_name("Memory Used")
        mem_used.set_type("int")
        mem_used.set_value(0)
        root.add_child(mem_used)

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
    RaspberryPiDSLink(Configuration("raspberry-pi", responder=True))
