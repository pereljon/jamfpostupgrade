# jamfpostupgrade
Launchdaemon installed when doing a Casper initiated OS upgrade (Mavericks to Yosemite)
Prior to upgrade, cache any packages which need to be installed post upgrade.
jamfpostupgrade will install all cached packages on first boot after the upgrade.

- Unloads loginwindow
- Checks JSS connection
- Update management
- Remove OS Install Data (if it wasn't cleaned up)
- Remove iPhoto
- Install cached packages
- Software update
- Fix ByHost files
- Fix dock
- Update inventory
- Fix permissions
- Script auto-destruct
- Reboot