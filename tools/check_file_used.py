import sys
import psutil
import traceback


class CheckFileUsed:
    def __init__(self, to_check_key):
        self.to_check_key = to_check_key

    def do_work(self):
        pids = psutil.pids()
        for pid in pids:
            try:
                p = psutil.Process(pid)
                for f in p.open_files():
                    if f.path.count(self.to_check_key):
                        print("[%s][%s][%s]" % (pid, p.name(), f.path))
            except Exception as e:
                #traceback.print_exc()
                #raise
                print("%s: %s" % (e, p.name()))
                pass


if __name__ == "__main__":
    c = CheckFileUsed(sys.argv[1])
    c.do_work()
