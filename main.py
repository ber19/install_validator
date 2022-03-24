from cli_args import get_args
from xml_process import Xml


def main():
    args = get_args()
    xml = Xml()
    nodes = xml.start()

    if args.extract:
        xml.extract_jobs()
    if args.accommodate:
        xml.accommodate(nodes["xml"])
    if args.check_sentry:
        xml.checkSentry(nodes)
    
if __name__ == "__main__":
    main()