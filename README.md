This is a fork of https://github.com/charmedlabs/vizy, only containing files needed to manage Vizy's power board and control its fan.  It's originally set up for breathecam, but could be generally useful if you're building your own software stack for vizy.

Fan speeds are a little more aggressive in hopes it might help warm the front glass during wintertime?  (Untested whether this helps.)

Dip switches are overridden to ensure automatic power on (change in PowerMonitor.set_dip_switches)

Installation:

    cd ~
    git clone https://github.com/CMU-CREATE-Lab/vizy-power-monitor-standalone.git
    vizy-power-monitor-standalone/install.py

To do:

* Consider having handle_timesync() write to the RTC once a day to correct for drift
