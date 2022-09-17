This is a fork of https://github.com/charmedlabs/vizy, only containing files needed to manage Vizy's power board and control its fan.  It's originally set up for breathecam, but could be generally useful if you're building your own software stack for vizy.

Fan speeds are a little more aggressive in hopes we can better warm the rest of the box during wintertime

Installation:

    cd ~
    git clone https://github.com/CMU-CREATE-Lab/vizy-power-monitor-standalone.git
    vizy-power-monitor-standalone/install.py
    raspi-config / interface / turn on i2c
