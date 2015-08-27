#!/usr/bin/python
""" jamfpostupgrade.py - run after os upgrade
    Author: Jonathan Perel
    Date: August 21, 2015"""

import sys
import os
import exceptions
import subprocess
import shutil
import logging
import time


def execute_command(command):
    """Execute system command"""
    logging.debug('executeCommand: %s', ' '.join(command))
    try:
        result = subprocess.check_output(command)
        logging.debug('Result: %s', result)
    except subprocess.CalledProcessError as error:
        logging.error('Return code: %s.', error.returncode)
        logging.error('Output: %s.', error.output)
    except exceptions.OSError as error:
        logging.critical('OS Error: #%s: %s', error.errno, error.strerror)
        sys.exit(1)
    else:
        return result


def jamf_helper(window_type, title=None, heading=None, description=None, icon=None, position=None, button1=None):
    """Use jamfhelper to open a window"""
    logging.info('Jamf Helper: %s', window_type)
    jamf_helper_path = '/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper'
    jamf_helper_types = ['hud', 'utility', 'fs', 'kill']
    jamf_helper_positions = ['ul', 'll', 'ur', 'lr', None]
    jamf_helper_alignment = ['right', 'left', 'center', 'justified', 'natural', None]

    # Error checking
    if not os.path.exists(jamf_helper_path):
        logging.error('JAMF helper not found.')
        return
    if window_type not in jamf_helper_types:
        logging.critical('Bad window type: %s', window_type)
        sys.exit(1)
    if window_type == 'fs' and button1 is not None:
        logging.critical('Fullscreen window with button')
        sys.exit(1)
    if position not in jamf_helper_positions:
        logging.critical('Bad position type: %s', position)
        sys.exit(1)

    if window_type == 'kill':
        # Kill the jamfHelper process to remove fullscreen window
        logging.debug('Killing jamfhelper')
        execute_command(['pkill', 'jamfHelper'])
        return
    # Options
    options = ['-windowType', window_type]
    if title is not None:
        options = options + ['-title', title]
    if heading is not None:
        options = options + ['-heading', heading]
    if description is not None:
        options = options + ['-description', description]
    if icon is not None:
        options = options + ['-icon', icon]
    if position is not None:
        options = options + ['-windowPosition', position]
    if window_type == 'hud':
        options = options + ['-lockHUD']
    if button1 is not None:
        options = options + ['-button1', button1]
    # Concatenate command
    command = [jamf_helper_path] + options
    # Execute command
    jamf_helper('kill')
    p = subprocess.Popen(command)
    if button1 is not None:
        # Wait for button to be pressed
        p.wait()


def main():
    logging.basicConfig(filename='/Library/Application Support/JAMF/logs/jamfpostupgrade.log', level=logging.DEBUG)

    # Sleep for 30
    time.sleep(30)

    # Unload loginwindow
    logging.info('Unload loginwindow')
    execute_command(['launchctl', 'unload', '/System/Library/LaunchDaemons/com.apple.loginwindow.plist'])

    # Checking JSS connection
    logging.info('Checking JSS connection')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Checking JSS connectiont')
    result = execute_command(['jamf', 'checkJSSConnection'])
    logging.debug(result)

    # Update management
    logging.info('Update management')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Update management')
    result = execute_command(['jamf', 'manage', '-verbose'])
    logging.debug(result)

    # Remove OS Install Data
    logging.info('Remove OS X Install Data folder')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Remove OS X Install Data folder')
    shutil.rmtree('/OS X Install Data', ignore_errors=True)

    # Remove iPhoto
    logging.info('Remove iPhoto')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Remove iPhoto')
    shutil.rmtree('/Applications/iPhoto.app', ignore_errors=True)

    # Install cached packages
    logging.info('Installing cached packages')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Install cached packages')
    result = execute_command(['/usr/sbin/jamf', 'installAllCached'])
    logging.debug(result)

    # Software update
    logging.info('Software update')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Software update')
    result = execute_command(['/usr/sbin/softwareupdate', '-ia'])
    logging.debug(result)

    # Fix ByHost files
    logging.info('Fix ByHosts file')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Fix ByHost files')
    result = execute_command(['/usr/sbin/jamf', 'fixByHostFiles', '-target', '/'])
    logging.debug(result)

    # Fix dock
    logging.info('Fix docks')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Fix dock')
    result = execute_command(['/usr/sbin/jamf', 'fixDocks'])
    logging.debug(result)

    # Update inventory
    logging.info('Update inventory')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Update inventory')
    result = execute_command(['/usr/sbin/jamf', 'recon'])
    logging.debug(result)

    # Fix permissions
    logging.info('Fix permissions')
    jamf_helper(window_type='fs', heading='Post upgrade:', description='Fix permissions')
    result = execute_command(['/usr/sbin/jamf', 'fixPermissions', '-target', '/'])
    logging.debug(result)

    # Kill jamfHelper
    jamf_helper('kill')

    # Delete launchdaemon
    if os.path.exists('/Library/LaunchDaemons/com.github.jamfpostupgrade.plist'):
        logging.info('Remove launchdaemon')
        os.remove('/Library/LaunchDaemons/com.github.jamfpostupgrade.plist')

    # Load loginwindow0
    #logging.info('Load loginwindow')
    #execute_command(['launchctl', 'load', '/System/Library/LaunchDaemons/com.apple.loginwindow.plist'])

    # Script auto-destruct
    # logging.info('Script auto-destruct')
    execute_command(['srm', sys.argv[0]])
    execute_command(['reboot'])


# MAIN
if __name__ == '__main__':
    main()
    sys.exit(0)
