#!/usr/bin/env python3

import requests
import os, sys
import re
import logging


try:
    import apt.cache
    import apt.debfile
except ImportError:
    logging.error("Sorry, must install the apt package to run this program.")
    logging.error("Use: sudo apt-get install python3-apt python3-distutils-extra.")
    sys.exit(1)


class Plex:
    def __init__(self, token = None, server_ip = "127.0.0.1", logging_level="INFO"):
        self.log_level = self.logging_config(logging_level)
        self.token = token
        self.server_ip = server_ip
        self.update_url = "https://plex.tv/downloads/latest/5?channel=8&build=linux-x86_64&distro=debian&X-Plex-Token=" + str(self.token)
        self.url = "http://" + self.server_ip + ":32400/status/sessions"
        self.location_download = os.path.dirname(os.path.realpath(__file__)) + "/plex_download.deb"
        self.deb_downloaded = self.download_deb_from_plex()
        self.current_sessions = int(self.lookup_sessions())
        self.condition_soft_version = 0
        self.allow_soft_update = self.condition_soft_update()

    def logging_config(self, logging_level):
        logfile = os.getcwd() + '/plex_update.log'

        logging.basicConfig(filename=logfile, filemode='a', format='%(asctime)s %(levelname)s:%(message)s', level=logging_level)

        if not os.path.isfile(logfile):
            os.mknod(logfile)
            logging.info('plex log file created!')


        logging.debug('logging_config done!')
        logging.debug('LogFile:' + logfile)
        return logging_level
           
    def download_deb_from_plex(self):
        logging.debug('Start download deb file from: ' + self.update_url)
        r = requests.get(self.update_url, allow_redirects=True)
        try:
            open(self.location_download, 'wb').write(r.content)
            logging.info('Plex update downloaded to location: ' + self.location_download)
        except:
            logging.error('Failed to download file to: ' + self.location_download)
        finally:
            return os.path.isfile(self.location_download)
    
    def condition_soft_update(self):
        if (self.has_active_session()) and (self.deb_downloaded):
            self.condition_soft_version = self.compare_pacakge_versions()
            if self.condition_soft_version == 3:
                logging.info('All conditions are fine. We can update our software')
            elif self.condition_soft_version == 0:
                logging.warning('Failed match versions. Is there any plex installed?')
            else:
                logging.info('Downloaded version isnt newer than the installed one.')
        return self.condition_soft_version == 3

    def lookup_sessions(self):
        
        try:
            r = requests.get(self.url, timeout=0.5 )
            session = re.findall(r'size=("\d")', r.text)[0].replace('"', "")
        except:
            logging.error('We dont have connection with plex server.')
            session = 999
        logging.debug('Active sessions: ' + str(session)) 
        return session
        
    def has_active_session(self):
        return self.current_sessions == 0
    
    def compare_pacakge_versions(self):
        '''
        VERSION_NEWER = 3
        VERSION_NONE = 0
        VERSION_OUTDATED = 1
        VERSION_SAME = 2
        '''
        version_code = apt.debfile.DebPackage(self.location_download).compare_to_version_in_cache()
        logging.debug('compare_pacakge_versions: ' + str(version_code))
        return version_code
    
    def pkg_install(self):
        if self.allow_soft_update:
            logging.debug('Install plex with newer version')
            apt.debfile.DebPackage(self.location_download).install(install_progress=False)
            if os.system('systemctl status plexmediaserver') != 0:
                logging.error("Warning. plexmediaserver failed to load.")
        return self.allow_soft_update and self.compare_pacakge_versions() == 2 


plex = Plex(server_ip="127.0.0.1", logging_level='INFO')
if plex.pkg_install():
    logging.info('Plex server updated. Have fun with the new version.')
logging.debug(plex.__dict__)

