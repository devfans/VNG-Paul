#!/usr/bin/env python

import os
import ConfigParser
import signal
import logging


def parseConfig(options):
    config = ConfigParser.SafeConfigParser()
    config.read(options.config_file)
    config.set("general", "config_file", os.path.abspath(options.config_file))
    return config

def checkPid(pid):
    """ Check For the existence of a unix pid. """
    if pid < 0:
        return False

    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def killPid(pid, force=False):
    """ Check For the existence of a unix pid. """
    if pid < 0:
        return False

    try:
        os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
    except OSError:
        return False
    else:
        return True


if __name__ == "__main__":
    import os
    import argparse
    import subprocess
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(prog='pual.py')
    parser.add_argument('-c', '--config', action='store', dest='config_file', default='paul.conf')

    subparsers = parser.add_subparsers(title='subcommands', description='supported subcommands', dest='subcommand')
    start_parser = subparsers.add_parser('start', help='start paul')
    start_parser.add_argument('--debug', action='store_true', default=False)

    status_parser = subparsers.add_parser('status', help='check paul status')
    stop_parser = subparsers.add_parser('stop', help='stop paul')

    args = parser.parse_args()

    config = parseConfig(args)
    pid_file = config.get('general', 'pid_file')
    log_file = config.get('general', 'log_file')
    port = config.getint('general', 'port')

    if args.subcommand == 'start':
        if not args.debug:
            logging.basicConfig(level=logging.INFO)
        with open(log_file, "w") as flog:
            proc = subprocess.Popen(["/usr/bin/python2.7", "Serving.py", "--port=" + str(port), "--debug=" + str(args.debug), \
            "--config_file=" + args.config_file], stdout=flog, stderr=subprocess.STDOUT)
            pf = open(pid_file, 'w')
            pf.write(str(proc.pid))
            pf.flush()
            pf.close()

            print "Paul is started..."

    elif args.subcommand == 'stop':
        try:
            pid = int(open(pid_file).readline())
            killPid(pid, True)
            print "Paul running with pid %s is stopped." % pid
        except Exception as e:
            print(str(e))

        print "Paul is stopped."

    elif args.subcommand == 'status':
        try:
            pid = int(open(pid_file).readline())
            if checkPid(pid):
                print "Paul is running with pid %s." % pid
        except Exception as e:
            print str(e)
        print "Checking done!"

    else:
        print "Invalid subcommand!"
