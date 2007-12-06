%define name tuxsetup
%define version 1.1.0010
%define release %mkrel 1
%define distname %{name}-%{version}-final

%define _requires_exceptions libbabtts.so

Summary: Daemons and applications for Tux Droid
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{distname}.tar.gz
License: GPL/Acapela
Group: Toys
Url: http://www.tuxisalive.com/developer-corner/software/tuxsetup/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
ExclusiveArch: %{ix86}

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

%build

%install
rm -rf %{buildroot}
cp -a mirror %{buildroot}
mv %{buildroot}/usr/local/bin %{buildroot}%{_bindir}
rm -f %{buildroot}%{_docdir}/%{name}/COPYING 
#- copyrighted file
rm -f %{buildroot}/opt/tuxdroid/apps/tuxgi/sounds/9.wav
#- move udev rules after main Mandriva rules,
#- so that pam_console_apply does not modify device permissions while tuxd is running
#- or else some race will prevent tuxd from accessing the device
mv %{buildroot}%{_sysconfdir}/udev/rules.d/{45,55}-tuxdroid.rules

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

%clean
rm -rf %{buildroot}

%post
%update_menus

%postun
%clean_menus

%files
%defattr(-,root,root)
%doc ACAPELALICENSE CHANGES README
%{_bindir}/tux*
%{_sysconfdir}/udev/rules.d/*-tuxdroid.rules
%{_datadir}/applications/tux*.desktop
%{_datadir}/mime/tuxgadgetframework.xml
%{_datadir}/pixmaps/tux*.png
/opt/Acapela
/opt/tuxdroid
