from dapnet.api import DapnetApi

if __name__ == "__main__":
    dapcli = DapnetApi()
    ver = dapcli.get_version()
    print(ver)
