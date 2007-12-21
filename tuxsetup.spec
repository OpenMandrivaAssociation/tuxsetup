%define name tuxsetup
%define version 1.2.0037
%define release %mkrel 1
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
Patch1: tuxsetup-1.2.0037-final-use_helper.patch
License: GPL/Acapela
Group: Toys
Url: http://www.tuxisalive.com/developer-corner/software/tuxsetup/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
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
%patch1 -p1
chmod +x mirror/opt/tuxdroid/bin/tuxgdgmaker
ln -sf /opt/tuxdroid/bin/tuxgdgmaker mirror/usr/local/bin/tuxgdgmaker

%build

%install
rm -rf %{buildroot}
cp -a mirror %{buildroot}
mv %{buildroot}/usr/local/bin %{buildroot}%{_bindir}
#- add link for dfu-programmer (see scripts/postinst)
ln -nsf /opt/tuxdroid/bin/dfu-programmer %{buildroot}%{_bindir}/dfu-programmer
#- fix perms of images
chmod a+r %{buildroot}%{_datadir}/pixmaps/*.png

rm -f %{buildroot}%{_docdir}/%{name}/COPYING 
#- copyrighted file
rm -f %{buildroot}/opt/tuxdroid/apps/tuxgi/sounds/9.wav
#- move udev rules after main Mandriva rules,
#- so that pam_console_apply does not modify device permissions while tuxd is running
#- or else some race will prevent tuxd from accessing the device
mv %{buildroot}%{_sysconfdir}/udev/rules.d/{45,55}-tuxdroid.rules

#- fix shebangs
sed -i 's,^#/bin/,#!/bin/,' %{buildroot}/opt/tuxdroid/bin/tux*

#- consolehelper config: do not ask for password
for program in tuxgdg tuxgdgmaker; do
    mkdir -p %{buildroot}%{_sbindir}
    mv %{buildroot}%{_bindir}/$program %{buildroot}%{_sbindir}/$program
    ln -s %{_bindir}/consolehelper %{buildroot}%{_bindir}/$program
    mkdir -p %{buildroot}%{_sysconfdir}/pam.d/
    ln -sf %{_sysconfdir}/pam.d/mandriva-console-auth %{buildroot}%{_sysconfdir}/pam.d/$program
    mkdir -p %{buildroot}%{_sysconfdir}/security/console.apps/
    cat > %{buildroot}%{_sysconfdir}/security/console.apps/$program <<EOF
PROGRAM=/usr/sbin/$program
FALLBACK=false
SESSION=true
EOF
done

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
ENV{TUXDROID}=="1", RUN+="/bin/sh -c '/etc/dynamic/scripts/tuxdroid.script &>/dev/null &'"
EOF

#- do not modify firmware files by converting EOL
export DONT_FIX_EOL=1
# does not work because fix-eol matches on basename, not full path
# export EXCLUDE_FROM_EOL_CONVERSION=`find %{buildroot}/opt/tuxdroid/firmware/ -type f`

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
%{_sbindir}/tux*
%{_sysconfdir}/pam.d/tux*
%{_sysconfdir}/security/console.apps/tux*
%{_sysconfdir}/udev/rules.d/*-tuxdroid*.rules
%{_sysconfdir}/dynamic/scripts/tuxdroid.script
%{_sysconfdir}/dynamic/launchers/tuxdroid
%{_datadir}/applications/tux*.desktop
%{_datadir}/mime/tuxgadgetframework.xml
%{_datadir}/pixmaps/*.png
/opt/Acapela
/opt/tuxdroid
