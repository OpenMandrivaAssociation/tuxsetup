%define name tuxsetup
%define version 1.1.0010
%define release %mkrel 3
%define distname %{name}-%{version}-final

%define _requires_exceptions libbabtts.so

Summary: Daemons and applications for Tux Droid
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{distname}.tar.gz
# use root supplementary group to be able to access USB devices
# when running tuxd from udev
Patch0: tuxsetup-1.1.0010-final-suppl_group.patch
License: GPL/Acapela
Group: Toys
Url: http://www.tuxisalive.com/developer-corner/software/tuxsetup/
ExclusiveArch: %{ix86}
Requires: dynamic
Requires: python-pyxml
Requires: pygtk2.0-libglade

%description
tuxsetup contains daemons and applications for the Tux Droid wireless robot:
- tuxd, the tux daemon
- tuxttsd, the tux text to speech daemon
- the python API
- the gadget manager
- a few gadgets: weather, clock and emial gagdet
- tuxgi, tux droid graphical interface
- original sound files
- latest firmware

%prep
%setup -q -n %{distname}
%patch0 -p1

%build

%install
rm -rf %{buildroot}
cp -a mirror %{buildroot}
mv %{buildroot}/usr/local/bin %{buildroot}%{_bindir}
#- add link for dfu-programmer (see scripts/postinst)
ln -nsf /opt/tuxdroid/bin/dfu-programmer %{buildroot}%{_bindir}/dfu-programmer

rm -f %{buildroot}%{_docdir}/%{name}/COPYING 
#- copyrighted file
rm -f %{buildroot}/opt/tuxdroid/apps/tuxgi/sounds/9.wav
#- move udev rules after main Mandriva rules,
#- so that pam_console_apply does not modify device permissions while tuxd is running
#- or else some race will prevent tuxd from accessing the device
mv %{buildroot}%{_sysconfdir}/udev/rules.d/{45,55}-tuxdroid.rules

#- consolehelper config: do not ask for password
mkdir -p %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/tuxgdg %{buildroot}%{_sbindir}/tuxgdg
ln -s %{_bindir}/consolehelper %{buildroot}%{_bindir}/tuxgdg
mkdir -p %{buildroot}%{_sysconfdir}/pam.d/
ln -sf %{_sysconfdir}/pam.d/mandriva-console-auth %{buildroot}%{_sysconfdir}/pam.d/tuxgdg
mkdir -p %{buildroot}%{_sysconfdir}/security/console.apps/
cat > %{buildroot}%{_sysconfdir}/security/console.apps/tuxgdg <<EOF
PROGRAM=/usr/sbin/tuxgdg
FALLBACK=false
SESSION=true
EOF

cat > %{buildroot}%{_datadir}/applications/tuxgi.desktop << EOF
[Desktop Entry]
Name=Tux Droid Interface
Comment=Tux Droid graphical interface
Exec=tuxgi
Icon=tuxmanager
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=true
EOF

install -d %{buildroot}%{_sysconfdir}/dynamic/launchers/tuxdroid
for desktop in kde gnome; do
  ln -sf ../../../../%{_datadir}/applications/tuxgi.desktop \
    %{buildroot}%{_sysconfdir}/dynamic/launchers/tuxdroid/$desktop.desktop
done

install -d %{buildroot}%{_sysconfdir}/dynamic/scripts
cat > %{buildroot}%{_sysconfdir}/dynamic/scripts/tuxdroid.script << EOF
#!/bin/sh
. /etc/dynamic/scripts/functions.script
check_activated \$0
call_hooks \$ACTION tuxdroid \$DEVNAME ""
EOF
chmod +x %{buildroot}%{_sysconfdir}/dynamic/scripts/tuxdroid.script

cat > %{buildroot}%{_sysconfdir}/udev/rules.d/65-tuxdroid-dynamic.rules << EOF
# Dynamic rules for tuxdroid
SUBSYSTEM=="usb_device", SYSFS{idVendor}=="03eb", SYSFS{idProduct}=="ff07", ENV{TUXDROID}="1"
ENV{TUXDROID}=="1", RUN+="/bin/sh -c '/etc/dynamic/scripts/tuxdroid.script &'"
EOF

%clean
rm -rf %{buildroot}

%post
%update_menus

%postun
%clean_menus

%files
%defattr(-,root,root)
%doc ACAPELALICENSE CHANGES README
%{_bindir}/dfu-programmer
%{_bindir}/tux*
%{_sbindir}/tuxgdg
%{_sysconfdir}/pam.d/tuxgdg
%{_sysconfdir}/security/console.apps/tuxgdg
%{_sysconfdir}/udev/rules.d/*-tuxdroid*.rules
%{_sysconfdir}/dynamic/scripts/tuxdroid.script
%{_sysconfdir}/dynamic/launchers/tuxdroid
%{_datadir}/applications/tux*.desktop
%{_datadir}/mime/tuxgadgetframework.xml
%{_datadir}/pixmaps/tux*.png
/opt/Acapela
/opt/tuxdroid
