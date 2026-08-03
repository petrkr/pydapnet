import dapnet

if __name__ == "__main__":
    dapcli = dapnet.DapnetClient()
    ver = dapcli.get_version()
    print(ver)
