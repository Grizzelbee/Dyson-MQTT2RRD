#!/usr/bin/env python
# Copyright 2014 David Irvine
#
# This file is part of MQTT2RRD
#
# MQTT2RRD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MQTT2RRD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MQTT2RRD.  If not, see "http://www.gnu.org/licenses/".
#
import sys, os, argparse, atexit, time, logging, configparser, grp, pwd, getpass, json
from signal import SIGTERM
#import mosquitto, rrdtool
import paho.mqtt.client as paho, rrdtool
import pprint

logger=logging.getLogger("MQTT2RRD")

config = configparser.RawConfigParser()


def get_config_item(section, name, default):
    """
    Gets an item from the config file, setting the default value if not found.
    """
    try:
        value = config.get(section, name)
    except:
        value = default
    return value


def extract_float(pl):
    """
    Tries to find a float value in the message payload.
    """
    try:
        return float(pl)
    except ValueError:
        pass

    try:
        return float(pl.split(" ")[0])
    except ValueError:
        pass

    return None


####
#
#  Sub Command Handlers, called for each command specified in arg parser config
#
####
def start(args, daemon):
    """
        Starts logging, either as a daemon or in the foreground.
    """
    # Check the data directory exists
    data_dir = get_config_item("daemon", "data_dir", "/var/lib/mqtt2rrd", )
    if not os.path.isdir(data_dir):
        logger.critical(
            "%s: Error: data directory %s does not exist or is not a directory\n" % (sys.argv[0], data_dir))
        sys.exit(1)

    if args.no_daemon:
        run(args)
    else:
        daemon.start(args)

def stop(args, daemon):
    daemon.stop()


def restart(args, daemon):
    daemon.restart(args, daemon)


def run(args):
    """
    Initiates the MQTT connection, and starts the main loop
    Is called by either the daemon.start() method, or the start function
    if the no-daemon option is specified.
    """
    while(True):
        try:
            logger.debug("Entering Loop")
            client = paho.Client(get_config_item("mqtt", "client_id", "MQTT2RRD Client"))
            client.on_message = on_message
            client.on_connect = on_connect

            if get_config_item("mqtt", "username", None):
                client.username_pw_set(
                    get_config_item("mqtt", "username", ""),
                    get_config_item("mqtt", "password", ""),
                )
            logger.debug("Attempting to connect to server: %s:%s" % (get_config_item("mqtt", "hostname", "localhost"), get_config_item("mqtt", "port", 1833),))
            client.connect(
                get_config_item("mqtt", "hostname", "localhost"),
                port=int(get_config_item("mqtt", "port", 1883)),
                keepalive=int(get_config_item("mqtt", "keepalive", 60)),
            )
            logger.info("Connected: %s:%s" % (get_config_item("mqtt", "hostname", "localhost"), get_config_item("mqtt", "port", 1833),))
            client.loop_forever()
        except Exception as e:
            logging.critical("FAIL: %s" % str(e))
            time.sleep(30) # 30 second wait


####
#
# MQTT Callback handlers
#
####
def on_connect(client, userdata, rc):
    logger.info("status" + str(rc))
    logger.info("Connected to server.")
    subs = get_config_item("mqtt", "subscriptions", "#")
    for i in subs.split(","):
        logger.info("Subscribing to topic: %s" % i)
        client.subscribe(i)


def on_message(mosq, obj, msg):
    logger.debug("Message received on topic: %s with payload: %s." % (msg.topic, msg.payload))

    jsonstr = str(msg.payload)[2:-1]
    data = json.loads(str(jsonstr))
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)
    
    if data['msg'] == 'CURRENT-STATE':
        for key, value in data['product-state'].items():
            rrdsave(key, value)
    elif data['msg'] == 'STATE-CHANGE':
        for key, value in data['product-state'].items():
            rrdsave(key, value[1])
    elif data['msg'] == 'ENVIRONMENTAL-CURRENT-SENSOR-DATA':
        for key, value in data['data'].items():
            rrdsave(key, value)
    elif data['msg'] == 'ENVIRONMENTAL-AND-USAGE-DATA':
        for key, value in data['data'].items():
            rrdsave(key, value)



######
#
# Save to database
#
######
def rrdsave(key, value):
    print ("Clef:" + key + " Valeur:" + value)
    file_name = key
    info_file_name = "%s.info" % file_name
    file_name = "%s.rrd" % file_name
    dir_name = get_config_item("daemon","data_dir","/var/lib/mqtt2rrd/")
    # TODO create dir

    #TODO create dictionary
    if value == 'ON':
        value = 1
    elif value == 'FAN':
        value = 1
    elif value == 'OFF':
        value = 0
        logger.info("%s is off" % ( key ));
        return
    elif value == 'NONE':
        value = 0
    elif value == 'AUTO':
        value = -1
    elif value == 'INIT':
        logger.info("%s is initialising" % ( key ));
        return
    if key == 'ercd':
        try:
            value = int(value, 16)
        except:
            logger.error("Could not convert Hex value of '%s' (%s)to int" % (key, value))

    try:
        pl = int(value)
    except:
        logger.error("Could not convert value of '%s' (%s)to int" % (key, value))
        return
    if pl != None:
        value = pl

    file_path = os.path.join(dir_name, file_name)
    graph_name = key
    if len(graph_name) > 19:
        graph_name = graph_name[:19]

    if key in ('fafs', 'faos', 'fofs', 'fons', 'vol0', 'vol1', 'vol2', 'vol3', 'vol4', 'vol5', 'vol6', 'vol7', 'vol8', 'vol9', 'pal0', 'pal1', 'pal2', 'pal3', 'pal4', 'pal5', 'pal6', 'pal7', 'pal8', 'pal9', 'aql0', 'aql1', 'aql2', 'aql3', 'aql4', 'aql5', 'aql6', 'aql7', 'aql8', 'aql9'):
        ds = "DS:%s:DERIVE:60:0:3600" % graph_name
    else:
        ds = "DS:%s:GAUGE:60:U:U" % graph_name
    ds = str(ds)

    if not os.path.exists(file_path):
        # Create the info file
        info={
            'topic':key,
            'created':time.time(),
            'friendly_name': get_config_item(key, "friendly_name", key)
        }
        info_fpath = os.path.join(dir_name, info_file_name)
        f=open(info_fpath, "w")
        json.dump(info, f)
        f.close()
        # Create the RRD file
        try:
            step=get_config_item(key, "step", 30)
            RRAstr = get_config_item(
                key,
                "archives",
                #"RRA:AVERAGE:0.5:2:30,RRA:AVERAGE:0.5:5:288,RRA:AVERAGE:0.5:30:336,RRA:AVERAGE:0.5:60:1488,RRA:AVERAGE:0.5:720:744,RRA:AVERAGE:0.5:1440:265"
                # 60s * 2    * 30   = 60 * 60           30 points toute les 2m      : 1h
                # 60s * 5    * 288  = 60 * 1440         288 points toute les 5m     : 24h
                # 60s * 30   * 336  = 60 * 10080        336 points toute les 30m    : 7 jours
                # 60s * 60   * 1448 = 60 * 86880        1448  points toute les 1h   : 60 jours
                # 60s * 720  * 744  = 60 * 535680       744 points toute les 12h    : 1an
                # 60s * 1440 * 265  = 60 * 381600       265 points toute les 24h    : <1an
                #"RRA:AVERAGE:0.5:1:120,RRA:AVERAGE:0.5:10:288,RRA:AVERAGE:0.5:60:336,RRA:AVERAGE:0.5:120:1488,RRA:AVERAGE:0.5:1440:744,RRA:AVERAGE:0.5:2880:744"
                # 30s * 1    * 120  = 60 * 60           120 points toute les 30s    : 1h
                # 30s * 10   * 288  = 60 * 1440         288 points toute les 5m     : 24h
                # 30s * 60   * 336  = 60 * 10080        336 points toute les 30m    : 7 jours
                # 30s * 120  * 1448 = 60 * 86880        1440  points toute les 1h   : 60 jours
                # 30s * 1440 * 744  = 60 * 535680       744 points toute les 12h    : 1an
                # 30s * 2880 * 265  = 60 * 381600       265 points toute les 24h    : <1an
                "RRA:AVERAGE:0.5:1:600,RRA:AVERAGE:0.5:10:372,RRA:AVERAGE:0.5:60:432,RRA:AVERAGE:0.5:120:1488,RRA:AVERAGE:0.5:1440:856,RRA:AVERAGE:0.5:2880:7534"

            )

            RRAs=[]
            for i in RRAstr.split(","):
                i=i.lstrip(" ")
                i=i.rstrip(" ")
                i=str(i)
                RRAs.append(i)

            logger.info("Creating RRD file: %s for topic: %s" % (file_path, key))
            rrdtool.create(str(file_path), "--step", str(step), "--start", "0", ds, *RRAs)

        except Exception as e:
            logger.error("Could not create RRD for topic: %s: %s" % (ds, e))
    try:
        logger.info("Updating: %s with value: %s" % (file_path, int(value)))
        rrdtool.update(str(file_path), str("N:%d" % value))
    except Exception as e:
        logger.error("Could not log value: %s to RRD %s for topic: %s: %s" % (value, file_path, key, e))

######
#
# Background process handlers
#
######
class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method

    Used with permission from Sander Marechal:
    http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

    """

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self, *args, **kwargs):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            logger.error(message % self.pidfile)
            sys.exit(1)
        # Start the daemon
        logger.debug("Daemonizing")
        self.daemonize()
        logger.debug("Running")
        self.run(*args, **kwargs)

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            logger.info(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                sys.exit(1)

    def restart(self, *args, **kwargs):
        """
        Restart the daemon
        """
        self.stop()
        self.start(*args, **kwargs)

    def run(self, *args, **kwargs):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """


class MQTTDaemon(Daemon):
    def run(self, *args, **kwargs):
        run(*args, **kwargs)


parser = argparse.ArgumentParser()
parser_subparsers = parser.add_subparsers(title='subcommands', description='Valid Commands',
                                   help='The following commands are available')


stop_parser = parser_subparsers.add_parser('stop')
stop_parser.set_defaults(func=stop)
stop_parser.add_argument("--config_file", help="The location of the config file", type=str, default="")

restart_parser = parser_subparsers.add_parser('restart')
restart_parser.add_argument("--config_file", help="The location of the config file", type=str, default="")
restart_parser.set_defaults(func=restart)

start_parser = parser_subparsers.add_parser('start')
start_parser.set_defaults(func=start)
start_parser.add_argument("--config_file", help="The location of the config file", type=str, default="")
start_parser.add_argument("--no_daemon", help="Do not spawn a daemon, stay in the foreground",
                          action="store_true", default=False)

args = parser.parse_args()

# Load configuration information
if len(args.config_file) > 0:
    config.read(args.config_file)
else:
    config.read(['/etc/mqtt2rrd.conf', os.path.expanduser('~/.mqtt2rrd.conf')])

formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')

logger.setLevel(int(get_config_item("logging", "log_level", "10")))
lf=get_config_item("logging", "log_file", None)
if lf:
    fh = logging.FileHandler(lf)
    fh.setLevel(int(get_config_item("logging", "log_level", "10")))
    fh.setFormatter(formatter)
    logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(int(get_config_item("logging", "log_level", "10")))
ch.setFormatter(formatter)
logger.addHandler(ch)



# Change to correct user if running as root.
user = get_config_item("daemon", "user", None)
group = get_config_item("daemon", "group", None)

if user and group and os.getuid() == 0:
    user = pwd.getpwnam(user).pw_uid
    group = grp.getgrnam(group).gr_gid

    os.setgid(group)
    os.setuid(user)


logger.info("Running as: %s" % getpass.getuser())

daemon = MQTTDaemon(get_config_item("daemon","pid_file","/var/run/mqtt2rrd.pid"))
logger.debug("Setup Daemon")
args.func(args, daemon)
