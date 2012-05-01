%global product_family Red Hat Enterprise Linux Hypervisor
%global mgmt_scripts_dir %{_sysconfdir}/node.d
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%global rhevh_build 28.1

Summary:        The RHEV Hypervisor daemons/scripts
Name:           ovirt-node
Version:        1.9.3
Release:        %{rhevh_build}%{?git}%{?dist}%{?extra_release}
Source0:        %{name}-%{version}-%{rhevh_build}.tar.gz

License:        GPLv2+
Group:          Applications/System

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL:            http://www.ovirt.org/
Requires(post):  /sbin/chkconfig
Requires(preun): /sbin/chkconfig
BuildRequires:  libvirt-devel >= 0.5.1
BuildRequires:  python-devel
BuildRequires:  python-setuptools
Requires:       libvirt >= 0.6.3
Requires:       augeas >= 0.3.5
#Requires:       libvirt-qpid >= 0.2.14-3
Requires:       udev >= 147-2.34
Requires:       wget
Requires:       cyrus-sasl-gssapi cyrus-sasl >= 2.1.22
Requires:       iscsi-initiator-utils
Requires:       ntp
Requires:       nfs-utils
Requires:       krb5-workstation
Requires:       bash
Requires:       chkconfig
Requires:       bind-utils
# Stupid yum dep solver pulls in older 'qemu' to resolve
# /usr/bin/qemu-img dep. This forces it to pick the new
# qemu-img RPM.
Requires:       qemu-img
Requires:       nc
Requires:       grub
Requires:       /usr/sbin/crond
Requires:       newt-python
Requires:       libuser-python >= 0.56.9
Requires:       dbus-python
#Requires:       python-IPy

ExclusiveArch:  x86_64

%define app_root %{_datadir}/%{name}

%description
Provides a series of daemons and support utilities for hypervisor distribution.

%package tools
Summary:        RHEV Hypervisor tools for building and running an RHEV Hypervisor image
Group:          Applications/System
BuildArch:      noarch
BuildRequires:  pykickstart  >= 1.54
Requires:       livecd-tools >= 020-2

%define tools_root %{_datadir}/ovirt-node-tools

%description tools
This package provides recipe (ks files), client tools,
documentation for building and running an RHEV Hypervisor image. This package
is not to be installed on the RHEV Hypervisor, however on a development machine
to help to build the image.

%prep
%setup -q

%build
%configure
make

%install
%{__rm} -rf %{buildroot}
make install DESTDIR=%{buildroot}

# FIXME move all installs into makefile
%{__install} -d -m0755 %{buildroot}%{_initrddir}
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/cron.hourly
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -d -m0755 %{buildroot}%{mgmt_scripts_dir}
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/cron.d
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/logrotate.d
# remove nodeadmin from el6 build
#%{__install} -d -m0755 %{buildroot}%{python_sitelib}/nodeadmin

%{__install} -p -m0755 scripts/node-config %{buildroot}%{_sysconfdir}/sysconfig

%{__install} -p -m0755 scripts/ovirt-awake %{buildroot}%{_initrddir}
%{__install} -p -m0755 scripts/ovirt-early %{buildroot}%{_initrddir}
%{__install} -p -m0755 scripts/ovirt %{buildroot}%{_initrddir}
%{__install} -p -m0755 scripts/ovirt-post %{buildroot}%{_initrddir}
%{__install} -p -m0755 scripts/ovirt-firstboot %{buildroot}%{_initrddir}

%{__install} -p -m0644 logrotate/ovirt-logrotate %{buildroot}%{_sysconfdir}/cron.d
%{__install} -p -m0644 logrotate/ovirt-logrotate.conf %{buildroot}%{_sysconfdir}/logrotate.d/ovirt-node

#dracut module for disk cleanup
%{__install} -d -m0755 %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0755 dracut/check %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0755 dracut/install %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0755 scripts/ovirt-boot-functions %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0755 dracut/ovirt-cleanup.sh %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode

mkdir -p %{buildroot}/%{_sysconfdir}/default
echo "# File where default configuration is kept" > %{buildroot}/%{_sysconfdir}/default/ovirt

# ovirt-config-boot post-install hooks
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/ovirt-config-boot.d
# default hook for local_boot_trigger
%{__install} -p -m0755 scripts/local_boot_trigger.sh %{buildroot}%{_sysconfdir}/ovirt-config-boot.d

# newt UI
%{__install} -d -m0755 %{buildroot}%{python_sitelib}/ovirt_config_setup
%{__install} -p -m0644 scripts/__init__.py %{buildroot}%{python_sitelib}/ovirt_config_setup
%{__install} -p -m0644 scripts/rhevm.py %{buildroot}%{python_sitelib}/ovirt_config_setup
%{__install} -p -m0644 scripts/rhn.py %{buildroot}%{python_sitelib}/ovirt_config_setup
%{__install} -d -m0755 %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/__init__.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/storage.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/password.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/install.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/iscsi.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/kdump.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/logging.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/ovirtfunctions.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/network.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0755 scripts/ovirt-config-installer.py %{buildroot}%{_libexecdir}/ovirt-config-installer
%{__install} -p -m0755 scripts/ovirt-config-setup.py %{buildroot}%{_libexecdir}/ovirt-config-setup
%{__install} -p -m0755 scripts/ovirt-admin-shell %{buildroot}%{_libexecdir}
# python-augeas is not in RHEL-6
%{__install} -p -m0644 scripts/augeas.py %{buildroot}%{python_sitelib}

# default ovirt-config-setup menu options
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/ovirt-config-setup.d
%{__ln_s} ../..%{_libexecdir}/ovirt-config-storage %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"00_Configure storage partitions"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-password %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"05_Configure authentication"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-hostname %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"10_Set the hostname"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-iscsi %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"12_iSCSI Initiator setup"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-networking %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"15_Networking setup"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-logging %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"17_Logging setup"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-kdump %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"20_Kdump Configuration"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-rhn %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"25_Register Host to RHN"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-snmp %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"26_Enable SNMP Agent"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-view-logs %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"90_View logs"
%{__ln_s} ../..%{_libexecdir}/ovirt-config-boot-wrapper %{buildroot}%{_sysconfdir}/ovirt-config-setup.d/"98_Install locally and reboot"

# ovirt-early vendor hook dir
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/ovirt-early.d


%clean
%{__rm} -rf %{buildroot}

%post
/sbin/chkconfig --add ovirt-awake
/sbin/chkconfig --add ovirt-early
/sbin/chkconfig --add ovirt-firstboot
/sbin/chkconfig --add ovirt
/sbin/chkconfig --add ovirt-post
# workaround for imgcreate/live.py __copy_efi_files
if [ ! -e /boot/grub/splash.xpm.gz ]; then
  cp -v /usr/share/ovirt-node/grub-splash.xpm.gz /boot/grub/splash.xpm.gz
else
  ls -lR /boot
fi

%preun
if [ $1 = 0 ] ; then
    /sbin/service ovirt-early stop >/dev/null 2>&1
    /sbin/service ovirt-firstboor stop >/dev/null 2>&1
    /sbin/service ovirt stop >/dev/null 2>&1
    /sbin/service ovirt-post stop >/dev/null 2>&1
    /sbin/chkconfig --del ovirt-awake
    /sbin/chkconfig --del ovirt-early
    /sbin/chkconfig --del ovirt-firstboot
    /sbin/chkconfig --del ovirt
    /sbin/chkconfig --del ovirt-post
fi


%files tools
%defattr(0644,root,root,0755)
%doc README COPYING
%{tools_root}/*.ks
%defattr(0755,root,root,0755)
%{_sbindir}/node-creator


%files
%defattr(-,root,root)
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/default/ovirt

%config(noreplace) %{_sysconfdir}/logrotate.d/ovirt-node
%config(noreplace) %{_sysconfdir}/cron.d/ovirt-logrotate

%{mgmt_scripts_dir}
%{_sysconfdir}/ovirt-config-boot.d
%{_sysconfdir}/ovirt-config-setup.d
%config(noreplace) %{_sysconfdir}/sysconfig/node-config

%doc COPYING
# should be ifarch i386
%{app_root}/grub-splash.xpm.gz
# end i386 bits
%{app_root}/syslinux-vesa-splash.jpg

%{_datadir}/dracut/modules.d/91ovirtnode/check
%{_datadir}/dracut/modules.d/91ovirtnode/install
%{_datadir}/dracut/modules.d/91ovirtnode/ovirt-boot-functions
%{_datadir}/dracut/modules.d/91ovirtnode/ovirt-cleanup.sh
%{_libexecdir}/ovirt-config-boot
%{_libexecdir}/ovirt-config-boot-wrapper
%{_libexecdir}/ovirt-config-hostname
%{_libexecdir}/ovirt-config-iscsi
%{_libexecdir}/ovirt-config-kdump
%{_libexecdir}/ovirt-config-logging
%{_libexecdir}/ovirt-config-networking
%{_libexecdir}/ovirt-config-password
%{_libexecdir}/ovirt-config-rhn
%{_libexecdir}/ovirt-config-setup
%{_libexecdir}/ovirt-config-setup-old
%{_libexecdir}/ovirt-config-snmp
%{_libexecdir}/ovirt-config-storage
%{_libexecdir}/ovirt-config-uninstall
%{_libexecdir}/ovirt-config-view-logs
%{_libexecdir}/ovirt-functions
%{_libexecdir}/ovirt-boot-functions
%{_libexecdir}/ovirt-install-node-stateless
%{_libexecdir}/ovirt-process-config
%{_libexecdir}/ovirt-rpmquery
%{_libexecdir}/ovirt-config-installer
%{_libexecdir}/ovirt-admin-shell
%{_sbindir}/gptsync
%{_sbindir}/showpart
%{_sbindir}/persist
%{_sbindir}/unpersist
%{python_sitelib}/ovirt_config_setup
%{python_sitelib}/ovirtnode
%{python_sitelib}/augeas*

%{_initrddir}/ovirt-awake
%{_initrddir}/ovirt-early
%{_initrddir}/ovirt-firstboot
%{_initrddir}/ovirt
%{_initrddir}/ovirt-post
%{_sysconfdir}/ovirt-early.d

%changelog
* Tue May 03 2011 Mike Burns <mburns@redhat.com> 1.9.3-28.1
- Fix encrypting of Swap2 rhbz#633587
- Fix grub device map for various usr/devmapper types rhbz#699602

* Wed Apr 27 2011 Mike Burns <mburns@redhat.com> 1.9.3-27.1
- Remove LANG=C and LC_ALL from /etc/profile rhbz#675823
- Move uninstall wipe of mbr to ovirt-early rhbz#626662
- Fix encrypted swap setup and parsing rhbz#633587
- Fix parsing for AppVG autoinstall rhbz#633583
- Fix grub installation to usb drives rhbz#699602

* Tue Apr 19 2011 Mike Burns <mburns@redhat.com> 1.9.3-26.2
- Fix looping in storage_init parsing rhbz#691891
- Prevent race by making /dev/disk/by-labels on install rhbz#696566
- Manually recreate /dev/mapper entries for partitions rhbz#696566
- Save default grub entries after successful reboot rhbz#696566
- Wipe disk after cleaning lvm info rhbz#626662
- Fix yum.Errors import error for RHN registration rhbz#696439
- Fix SELinux context for /boot-kdump rhbz#654565
- Fix kdump startup rhbz#654565
- Fix static networking bridge configuration rhbz#696512
- Correct certificate paths in vdsm.conf config rhbz#625083
- autoinstall/in-place upgrade breaks serial rhbz#696566

* Tue Apr 12 2011 Mike Burns <mburns@redhat.com> 1.9.3-25
- Enable ESC for aborting ISO media check rhbz#683330
- Fix ipv6 network configuration files rhbz#690792
- Add more debug logging for installation failures rhbz#694644
- Return true when persisting config files rhbz#690677
- Fix parted Root partition size rhbz#690762
- Block major version upgrades rhbz#588267
- Fix name in grub.conf rhbz#677534
- Fix dracut prompt during cleanup rhbz#692072

* Wed Apr 06 2011 Mike Burns <mburns@redhat.com> 1.9.3-24
- Fix name in plymouth progress bar rhbz#676784
- Fix ipv6 dhcp iprules entries rhbz#683354
- Fix cciss installation errors rhbz#681164
- Cleanup catching of failures in autoinstall rhbz#681938
- Support storage_init=<bus> in dracut plugin rhbz#691891
- Blacklist restorecond.desktop rhbz#679367
- Cleanup startup errors rhbz#675868
- Set admin password during autoinstall rhbz#681934
- Fix hostvg_init storage disks rhbz#681164
- Allow firstboot to run unconfined rhbz#647756
- enable en_US.UTF-8 locale in new UI rhbz#675823

* Thu Mar 31 2011 Mike Burns <mburns@redhat.com> 1.9.3-23.2
- Enable vlan config processing rhbz#681168
- Remove confirm password dialog from RHN setup rhbz#690673
- Cleanup installation kargs rhbz#640782
- Update crashkernel parameter rhbz#654565
- Fix installs to /dev/mapper devices rhbz#676255
- Fix prompt for input in dracut when cleaning old disks rhbz#692072

* Fri Mar 25 2011 Mike Burns <mburns@redhat.com> 1.9.3-22
- Replace shutil.copy with a system call rhbz#683864
- Fix detection of syslinux/isolinux rhbz#689834
- Don't allow network changes if registered to RHEVM rhbz#675874
- fix cciss installation issues rhbz#681164
- Update weak password warning message rhbz#682924
- Expand ipv6 fields to 25 chars and fix validation rhbz#681146
- Add dracut plugin for disk cleanup rhbz#688168
- return true if ovirt_store_config succeeds rhbz#690677

* Mon Mar 21 2011 Mike Burns <mburns@redhat.com> 1.9.3-21
- Include rhevm configuration plugin rhbz#682162
- Include plugin for RHEV-M registration  rhbz#625083 rhbz#682162
- Include plugin for RHN registration  rhbz#676006
- Only allow logged in user to unlock screen rhbz#675248
- Use multipath for all devices rhbz#676255
- Fix serial console access rhbz#676969
- fix ovirt.log generation rhbz#681128
- Unblock ipv6 dhcp responses rhbz#683354
- Persist Enable Password Authentication ssh option rhbz#685102
- Fix network page reset button rhbz#688851
- Remove duplicate crashkernel option from commandline rhbz#685130
- Don't allow major version upgrades through the installer rhbz#681128
- Blank nic gateway if not a valid IP address rhbz#688849

* Thu Mar 10 2011 Mike Burns <mburns@redhat.com> 1.9.3-20
- Include rhevm configuration plugin rhbz#682162
- Boot failed on cciss storage rhbz#681164
- Re-install failed to cleanup 5.x installations rhbz#676988
- dhcp was getting the incorrect gateway address rhbz#676775
- serial console not operating correctly rhbz#676969
- SSH configuration not persisted correctly rhbz#681100
- Include uninstall functionality rhbz#632491 rhbz#626662
- Autoinstall continues even if image installation fails rhbz#681938
- Autoinstall intermittently fails on multipath devices rhbz#682005
- RHEV-H UI fixes rhbz#683331 rhbz#682107 rhbz#681735 rhbz#681131 rhbz#681130 rhbz#634795 rhbz#676066 rhbz#667885 rhbz#631629

* Fri Feb 25 2011 Mike Burns <mburns@redhat.com> 1.9.3-19
- unblacklist utf8 locale rhbz#676105
- support lsb_release -r rhbz#676108
- Generalize fstype checks to any ext fs rhbz#676112
- Fix installer issues with unmounting/mounting of logging services rhbz#680421
- Fix firstboot menu appearing after installation rhbz#679655
- RHEV-H UI fixes rhbz#679428 rhbz#636366

* Mon Feb 21 2011 Alan Pevec <apevec@redhat.com> 1.9.3-18
- Include usbutils and lsscsi packages rhbz#642518
- update udev calls for new options rhbz#644341
- clean up dependencies for libguestfs-winsupport rhbz#641494
- Improved RHEV-H User Interface fixes rhbz#614460 rhbz#676747 rhbz#676775 rhbz#676786 rhbz#677207 rhbz#634797 rhbz#676749 rhbz#676987 rhbz#677543 rhbz#629884 rhbz#632095 rhbz#679013

* Thu Feb 10 2011 Alan Pevec <apevec@redhat.com> 1.9.3-17
- Install fails when second disk exists with PV rhbz#675755
- multipath config incorrect rhbz#676255
- HostVG selection page rhbz#675238 rhbz#675241
- kdump config should allow only one selected at a time rhbz#675245
- after cycling through entry fields button colors are changed rhbz#675247
- lock screen should only allow logged in user to unlock rhbz#675248
- add ipv6 validation for network interface configuration rhbz#675279
- Manual input of storage device rhbz#623782
- Issues with local console password access installation screen rhbz#667016
- RFE: systemtap-runtime inclusion rhbz#640977
- RFE: request to include pciutils package rhbz#642518
- Rollback changes in ovirt-node after udevadm info fix rhbz#644341
- Provide our CPE name in a new system file rhbz#674924

* Mon Jan 31 2011 Alan Pevec <apevec@redhat.com> 1.9.3-16
- fail to install the rhev-hypervisor rhbz#672176
- fail to partition storage rhbz#673017
- fail to unmount logging partition rhbz#647752
- VDSM port should be open by default rhbz#662418
- duplicate entries under /dev/mapper/  rhbz#633222
- add libguestfs into RHEV-H rhbz#641494
- Advanced Storage Configuration for automated installs rhbz#633583 rhbz#613663
- Add Encrypted Swap Support to RHEV-H rhbz#633587
- Downloading cert takes too long time when registering RHN rhbz#635578

* Mon Nov 15 2010 Alan Pevec <apevec@redhat.com> 1.9.3-15
- additional default boot parameters rhbz#647301 rhbz#647300 rhbz#630837
- include multipath in initramfs rhbz#627647
- handle invalid input when selecting storage device rhbz#647732
- partition when both HostVG and Root devices are defined rhbz#647693

* Wed Oct 27 2010 Alan Pevec <apevec@redhat.com> 1.9.3-14
- fix uninstall failure rhbz#626662
- fix iscsi partitioning rhbz#629503
- fix cron job for ovirt logrotate rhbz#578499
- include dosfstools in rhev-h rhbz#631795
- fix manual_input drive selection rhbz#623782
- fix disable hostvg enable option rhbz#625381
- fix e2label operation in livecd-iso-to-iscsi rhbz#632664
- check iscsi rootfs kernel version matches before installing rhbz#633654
- check valid ip on iscsi target rhbz#631685
- SELinux enforcing mode rhbz#634170
- fix kernel cmdline ssh_pwauth option rhbz#642835
- fix vlan id input regex rhbz#627106
- enable ovirt-config-kdump AUTO for auto install rhbz#627828
- fix removal of existing HostVG from separate install drive rhbz#625871
- Fix multipath translation on autoinstall rhbz#642376
- Cleanup auto-installation partitioning rhbz#634176
- "firstboot" parameter not working after failed install rhbz#633222
- fix udev_info calls rhbz#633238
- add nomodeset to default boot options rhbz#630837
- setsebool virt_use_nfs on rhbz#642209
- save ovirt_early boot parameter rhbz#630012
- rpm query replacement rhbz#625083
- add option to disable snmpd rhbz#614870

* Tue Aug 31 2010 Alan Pevec <apevec@redhat.com> 1.9.3-12.git0ffa622
- Local Install and reboot fails rhbz#613754

* Wed Aug 25 2010 Alan Pevec <apevec@redhat.com> 1.9.3-9.git8ecebef
- Local Install and reboot fails rhbz#613754
- When upgrading, grub entry for old version is not created rhbz#624741
- Cleanup boot menus rhbz#624799
- Remove references to ovirt-logrotate.conf rhbz#578499

* Wed Aug 18 2010 Mike Burns <mburns@redhat.com> 1.9.3-8.gitb16b938
- Include common-el6.ks in ovirt-node-tools package rhbz#622939
- Include common-minimizer.ks in ovirt-node-tools package rhbz#622939
- fix manual_input option for storage configuration rhbz#623782
- fix installation to dirty storage rhbz#623783
- backup entry not included in grub.conf rhbz#624741
- add missing scsi modules to fix booting issues rhbz#624781
- Cleanup boot menus rhbz#624799

* Tue Aug 10 2010 Mike Burns <mburns@redhat.com> 1.9.3-7.4.gitc41536c
- fix hang in ovirt-early on boot rhbz#621401
- prevent ovirt-firstboot from appearing every boot rhbz#621403
- Add new splash screen rhbz#622483
- Update makefile to include common-minimizer in ovirt-node-tools rhbz#622939
- Include common-el6.ks in ovirt-node-tools package rhbz#622939

* Wed Aug 04 2010 Alan Pevec <apevec@redhat.com> 1.9.3-6.3.gitc41536c
- add SNMPv3 support rhbz#614870
- add rhn_* boot parameters rhbz#607503
- fix race condition in partitioning rhbz#613698

* Thu Jul 29 2010 Alan Pevec <apevec@redhat.com> 1.9.3-5.git3a9e2d0
- preferred_names in lvm.conf not setup correctly rhbz#613679
- log_only: command not found rhbz#613673
- can not disable unwanted network interfaces rhbz#614195
- add rhn-virtualization rhbz#607503
- add net-snmp rhbz#614870
- complete blacklist with image-minimizer rhbz#616119
- add RHEV logo on boot screen rhbz#537167

* Wed Jul 14 2010 Alan Pevec <apevec@redhat.com> 1.9.3-4.gitf53c39c
- kdump support rhbz#578501
- do not allow persisting top-level folders rhbz#597218
- bugfixes 610171 605358 610180

* Wed Jun 30 2010 Alan Pevec <apevec@redhat.com> 1.9.3-3.gitd5f8007
- RHN registration rhbz#607503
- restrict in-place upgrade to minor releases rhbz#588267
- add vhostmd rhbz#588852
- provide CPE name rhbz#592425
- remove rpmdb from the image rhbz#596718
- add license manifest rhbz#601927
- fix startup issues rhbz#602444 rhbz#599014 rhbz#599199
- remove libvirt users prompt rhbz#602448
- remove unneeded services rhbz#586535 rhbz#586536 rhbz#586541
- fix auditd startup errors rhbz#586539
- fix read-only root rhbz#586547 rhbz#602719
- fix image installation rhbz#586548
- add sysfsutils package rhbz#599708
- fix IP address validation rhbz#602445
- disable password authentication by default rhbz#602446
- update ext3 filesystems to ext4 rhbz#606969

* Wed May 26 2010 Alan Pevec <apevec@redhat.com> 1.9.3-1.git988d065
- rebase to latest upstrem/rhel6-devel branch for RHEV-H 6.0 rhbz#586983

* Tue Apr 04 2010 Darryl L. Pierce <dpierce@redhat.com> - 1.9.2-1
- Updated autoconf environment.
- Allow persistence of empty configuration files.

* Wed Mar 24 2010 Darryl L. Pierce <dpierce@redhat.com> - 1.9.1-1
- Update ovirt-process-config to fail configs that are missing the field name or value.
- Updated build system will use Fedora 13 as the rawhide repo.
- Fixed ovirt-config-networking to not report success when network start fails.
- Reboot hangs on /etc [FIXED].
- Multipath translation performance improvements.
- Cleanup ROOTDRIVE when partitioning.
- Fix hang when cleaning dirty storage.
- The order of the oVirt SysVInit scripts has been changed.
-   ovirt-early -> ovirt-awake -> ovirt -> ovirt-post
- Fixes to the SysVINit scripts to name lifecycle methods propery.
- Added psmisc package.
- Added default KEYTAB_FILE name to /etc/sysconfig/node-config.
- Fixes to the persist and unpersist commands to handle already persisted files and directories.
- Duplicate NTP/DNS entries are rejected during network setup.

* Fri Mar 19 2010 Alan Pevec <apevec@redhat.com> 1.9.0-0.4
- remove conflicts with redhat-release

* Wed Mar 03 2010 Alan Pevec <apevec@redhat.com> 1.9.0-0.1
- Initial build for RHEL-6

* Wed Feb 12 2010 David Huff <dhuff@redhat.com> - 1.9.0
- New build
