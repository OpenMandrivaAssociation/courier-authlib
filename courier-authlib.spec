Name:		courier-authlib
Version:	0.65.0
Release:	2
Summary:	Courier authentication library
Group:		System/Servers
License:	GPL
URL:		http://www.courier-mta.org
Source0:	http://prdownloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2
Source1:	courier-authlib.sysconftool.m4
Source2:	courier-authlib.authdaemon-init
Patch0:		courier-authlib-0.65.sysconftool.patch
BuildRequires:	expect
BuildRequires:	libltdl-devel
BuildRequires:	gdbm-devel
BuildRequires:	openldap-devel
BuildRequires:	pam-devel
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
Obsoletes:	courier-imap-utils
Obsoletes:	libcourier-authlib0
Conflicts:	courier-imap <= 3.0.8

%description
The Courier authentication library provides authentication
services for other Courier applications.

This package contains the Courier authentication daemon and common
authentication modules:

 o authcustom
 o authpam
 o authpwd
 o authshadow
 o courierauthsaslclient
 o courierauthsasl

%package -n courier-authdaemon
Summary:	Courier authentication daemon
Group:		System/Servers
Requires:	%{name} = %{version}
Requires:	expect
Requires(pre):	rpm-helper

%description -n courier-authdaemon
This package contains the Courier authentication daemon.

%package userdb
Summary:	Userdb support for the Courier authentication library
Group:		System/Servers
Requires(pre):	%{name} = %{version}

%description userdb
This package installs the userdb support for the Courier
authentication library.  Userdb is a simple way to manage virtual
mail accounts using a GDBM-based database file.

Install this package in order to be able to authenticate with
userdb.

%package ldap
Summary:	LDAP support for the Courier authentication library
Group:		System/Servers
Requires(pre):	%{name} = %{version}
Obsoletes:	courier-imap-ldap

%description ldap
This package installs LDAP support for the Courier authentication
library. Install this package in order to be able to authenticate
using LDAP.

%package mysql
Summary:	MySQL support for the Courier authentication library
Group:		System/Servers
Requires(pre):	%{name} = %{version}
Obsoletes:	courier-imap-mysql

%description mysql
This package installs MySQL support for the Courier authentication
library. Install this package in order to be able to authenticate
using MySQL.

%package pgsql
Summary:	PostgreSQL support for the Courier authentication library
Group:		System/Servers
Requires(pre):	%{name} = %{version}
Obsoletes:	courier-imap-pgsql

%description pgsql
This package installs PostgreSQL support for the Courier
authentication library. Install this package in order to be able
to authenticate using PostgreSQL.

%package sqlite
Summary:	SQLite support for the Courier authentication library
Group:		System/Servers
Requires(pre):	%{name} = %{version}

%description sqlite
This package installs SQLite support for the Courier
authentication library. Install this package in order to be able
to authenticate using SQLite.

%package devel
Summary:	Development libraries for the Courier authentication library
Group:		Development/C
Requires:	%{name} = %{version}

%description devel
This package contains the development libraries and files needed
to compile Courier packages that use this authentication library.
Install this package in order to build the rest of the Courier
packages. After they are built and installed this package can be
removed. Files in this package are not needed at runtime.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p 0 -b .sysconftool

cp %{SOURCE1} .

%build
%configure2_5x \
    --with-syslog=MAIL \
    --disable-ltdl-install \
    --with-db=gdbm \
    --with-random=/dev/urandom \
    --with-mailuser=daemon \
    --with-mailgroup=daemon \
    --with-authdaemonrc=%{_sysconfdir}/courier/authdaemonrc \
    --with-authdaemonvar=%{_localstatedir}/lib/authdaemon \
    --with-makedatprog=%{_sbindir}/makedatprog \
    --with-userdb=%{_sysconfdir}/userdb \
    --with-pkgconfdir=%{_sysconfdir}/courier \
    --with-authuserdb \
    --with-authpam \
    --with-authldap \
    --with-authldaprc=%{_sysconfdir}/courier/authldaprc \
    --with-authpwd \
    --with-authshadow \
    --without-authvchkpw \
    --with-authpgsqlrc=%{_sysconfdir}/courier/authpgsqlrc \
    --with-authpgsql \
    --with-pgsql-libs=%{_libdir} \
    --with-pgsql-includes=%{_includedir}/pgsql \
    --with-authmysqlrc=%{_sysconfdir}/courier/authmysqlrc \
    --with-authmysql \
    --with-mysql-libs=%{_libdir} \
    --with-mysql-includes=%{_includedir}/mysql \
    --with-authcustom
%make
%make authinfo

%check
%{__make} check

%install
%makeinstall_std

# fix perms
chmod 755 %{buildroot}%{_localstatedir}/lib/authdaemon

install -d %{buildroot}%{_var}/run/authdaemon

install -m 755 sysconftool %{buildroot}%{_libdir}/courier-authlib/
install -m 755 authmigrate %{buildroot}%{_libdir}/courier-authlib/

install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/courier-authdaemon
mv %{buildroot}%{_libdir}/courier-authlib/authdaemond %{buildroot}%{_sbindir}/authdaemond

mv %{buildroot}%{_libdir}/courier-authlib/makedatprog %{buildroot}%{_sbindir}/makedatprog

# some utils...
install -m 755 authinfo %{buildroot}%{_sbindir}/
install -m 755 authdaemontest %{buildroot}%{_sbindir}/
install -m 755 liblock/lockmail %{buildroot}%{_sbindir}/
install -m 644 liblock/lockmail.1 %{buildroot}%{_mandir}/man1/

# A hack to provide libraries under libdir to be able to pick up them w/o adding
# courier-authlib to LD_LIBRARY_PATH
for file in %{buildroot}%{_libdir}/courier-authlib/*.so
do
    ln -s %{_libdir}/courier-authlib/`basename $file` %{buildroot}%{_libdir}/`basename $file`
done

# fix configuration
for file in %{buildroot}%{_sysconfdir}/courier/*.dist; do
    mv $file  %{buildroot}%{_sysconfdir}/courier/`basename $file .dist`
done
chmod 644 %{buildroot}%{_sysconfdir}/courier/*

perl -pi \
    -e "s|^authmodulelist=.*|authmodulelist=\"authpam authpwd authshadow\"|g;" \
    -e "s|^authmodulelistorig=.*|authmodulelistorig=\"authpam authpwd authshadow\"|g;" \
    %{buildroot}%{_sysconfdir}/courier/authdaemonrc

cat > README.mdv << EOF
ROSA RPM specific notes

Upgrade
------
Default upgrade procedure consists of shipping new configuration files with
.dist suffix, then running sysconftool script to merge with current
configuration. This packages ships new configuration files with their final
name instead, wich will be saved by rpm as .rpmnew if original ones have been
modified, and run sysconftools script during upgrade automatically.
EOF

%post -n courier-authdaemon
%{_libdir}/courier-authlib/authmigrate >/dev/null
if [ -f %{_sysconfdir}/courier/authdaemonrc.rpmnew ]; then
    %{_libdir}/courier-authlib/sysconftool %{_sysconfdir}/courier/authdaemonrc.rpmnew >/dev/null
fi
%_post_service courier-authdaemon

%preun -n courier-authdaemon
%_preun_service courier-authdaemon

%post userdb
%{_initrddir}/courier-authdaemon condrestart 1>&2;

%postun userdb
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%post ldap
%{_libdir}/courier-authlib/authmigrate >/dev/null
if [ -f %{_sysconfdir}/courier/authldaprc.rpmnew ]; then
    %{_libdir}/courier-authlib/sysconftool %{_sysconfdir}/courier/authldaprc.rpmnew >/dev/null
fi
%{_initrddir}/courier-authdaemon condrestart 1>&2;
    
%postun ldap
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%post mysql
%{_libdir}/courier-authlib/authmigrate >/dev/null
if [ -f %{_sysconfdir}/courier/authmysqlrc.rpmnew ]; then
    %{_libdir}/courier-authlib/sysconftool %{_sysconfdir}/courier/authmysqlrc.rpmnew >/dev/null
fi
%{_initrddir}/courier-authdaemon condrestart 1>&2;
    
%postun mysql
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%pre pgsql
%{_libdir}/courier-authlib/authmigrate >/dev/null

%post pgsql
%{_initrddir}/courier-authdaemon condrestart 1>&2;
    
%postun pgsql
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%pre sqlite
%{_libdir}/courier-authlib/authmigrate >/dev/null

%post sqlite
%{_initrddir}/courier-authdaemon condrestart 1>&2;
    
%postun sqlite
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%files
%defattr(-,root,root)
%doc README.mdv README README.authdebug.html README.html README_authlib.html
%doc NEWS COPYING* AUTHORS ChangeLog liblock/lockmail.html liblog/courierlogger.html
%dir %{_sysconfdir}/courier
%dir %{_libdir}/courier-authlib
%{_libdir}/courier-authlib/authmigrate
%{_libdir}/courier-authlib/authsystem.passwd
%{_libdir}/courier-authlib/sysconftool
%{_libdir}/courier-authlib/libcourierauthsaslclient.so.*
%{_libdir}/courier-authlib/libcourierauthsasl.so.*
%{_libdir}/courier-authlib/libcourierauthcommon.so.*
%{_libdir}/courier-authlib/libcourierauth.so.*
%{_libdir}/courier-authlib/libauthcustom.so.0
%{_libdir}/courier-authlib/libauthpam.so.0
%{_libdir}/courier-authlib/libauthpwd.so.0
%{_libdir}/courier-authlib/libauthshadow.so.0
%{_libdir}/courier-authlib/libauthpipe.so.0
%{_mandir}/man1/*

%files -n courier-authdaemon
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/courier/authdaemonrc
%{_sbindir}/authdaemond
%{_sbindir}/authdaemontest
%{_sbindir}/authenumerate
%{_sbindir}/authinfo
%{_sbindir}/authtest
%{_sbindir}/courierlogger
%{_sbindir}/lockmail
%{_sbindir}/authpasswd
%{_sbindir}/makedatprog
%{_initrddir}/courier-authdaemon
%{_localstatedir}/lib/authdaemon
%{_var}/run/authdaemon

%files userdb
%defattr(-,root,root)
%doc userdb/makeuserdb.html userdb/userdb.html userdb/userdbpw.html
%{_sbindir}/makeuserdb
%{_sbindir}/pw2userdb
%{_sbindir}/userdb
%{_sbindir}/userdb-test-cram-md5
%{_sbindir}/userdbpw
%{_libdir}/courier-authlib/libauthuserdb.so.0
%{_mandir}/man8/*userdb*

%files ldap
%defattr(-,root,root)
%doc README.ldap authldap.schema
%config(noreplace) %{_sysconfdir}/courier/authldaprc
%{_libdir}/courier-authlib/libauthldap.so.0

%files mysql
%defattr(-,root,root)
%doc README.authmysql.html README.authmysql.myownquery
%config(noreplace) %{_sysconfdir}/courier/authmysqlrc
%{_libdir}/courier-authlib/libauthmysql.so.0

%files pgsql
%defattr(-,root,root)
%doc README.authpostgres.html
%config(noreplace) %{_sysconfdir}/courier/authpgsqlrc
%{_libdir}/courier-authlib/libauthpgsql.so.0

%files sqlite
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/courier/authsqliterc
%{_libdir}/courier-authlib/libauthsqlite.so.0

%files devel
%defattr(-,root,root)
%doc authlib.html auth_*.html
%{_bindir}/courierauthconfig
%{_libdir}/courier-authlib/*.a
%{_libdir}/courier-authlib/*.so
%{_libdir}/*.so
%{_includedir}/*
%{_mandir}/man3/*




%changelog
* Thu Mar 17 2011 Oden Eriksson <oeriksson@mandriva.com> 0.63.0-6mdv2011.0
+ Revision: 645789
- relink against libmysqlclient.so.18

* Sat Jan 01 2011 Oden Eriksson <oeriksson@mandriva.com> 0.63.0-5mdv2011.0
+ Revision: 627218
- rebuilt against mysql-5.5.8 libs, again

* Thu Dec 30 2010 Oden Eriksson <oeriksson@mandriva.com> 0.63.0-4mdv2011.0
+ Revision: 626512
- rebuilt against mysql-5.5.8 libs

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 0.63.0-2mdv2011.0
+ Revision: 610162
- rebuild

* Fri Feb 26 2010 Guillaume Rousse <guillomovitch@mandriva.org> 0.63.0-1mdv2010.1
+ Revision: 512127
- update to new version 0.63.0

* Thu Feb 18 2010 Oden Eriksson <oeriksson@mandriva.com> 0.62.4-2mdv2010.1
+ Revision: 507481
- rebuild

* Thu Jul 23 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.62.4-1mdv2010.0
+ Revision: 399045
- new version

* Sun Jan 18 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.62.0-1mdv2009.1
+ Revision: 331022
- update to new version 0.62.0

* Mon Dec 08 2008 Oden Eriksson <oeriksson@mandriva.com> 0.61.1-1mdv2009.1
+ Revision: 311851
- 0.61.1
- use lowercase mysql-devel

* Sat Dec 06 2008 Oden Eriksson <oeriksson@mandriva.com> 0.61.0-3mdv2009.1
+ Revision: 311327
- rebuilt against mysql-5.1.30 libs

* Mon Sep 08 2008 Guillaume Rousse <guillomovitch@mandriva.org> 0.61.0-2mdv2009.0
+ Revision: 282763
- use a rebind mount instead of an hard link for postfix chroot (bug #43478)
- change initscript to re-mount the socket directory in postfix chroot, as hardlinks don't work between different filesystems

* Sat Sep 06 2008 Guillaume Rousse <guillomovitch@mandriva.org> 0.61.0-1mdv2009.0
+ Revision: 281748
- new version

* Fri Jul 04 2008 Guillaume Rousse <guillomovitch@mandriva.org> 0.60.6-1mdv2009.0
+ Revision: 231884
- new version

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Wed Dec 26 2007 Oden Eriksson <oeriksson@mandriva.com> 0.60.1-2mdv2008.1
+ Revision: 137976
- rebuilt against openldap-2.4.7 libs

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Dec 13 2007 Guillaume Rousse <guillomovitch@mandriva.org> 0.60.1-1mdv2008.1
+ Revision: 119234
- update to new version 0.60.1


* Mon Mar 05 2007 Guillaume Rousse <guillomovitch@mandriva.org> 0.59.1-2mdv2007.0
+ Revision: 133179
- more consistent init scripts
- export DEBUG_LOGIN variable before launching daemon, as it seems to trust environment more than its configuration file (fix #28354)
- new version

* Fri Jan 12 2007 Guillaume Rousse <guillomovitch@mandriva.org> 0.59-1mdv2007.1
+ Revision: 107889
- new version
- Import courier-authlib

* Wed Sep 20 2006 Guillaume Rousse <guillomovitch@mandriva.org> 0.58-9mdv2007.0
- enforce courierlogger options in init script
- add network dependencies in init script

* Thu Aug 31 2006 Guillaume Rousse <guillomovitch@mandriva.org> 0.58-8mdv2007.0
- fix sysconftool patch
- fix config file merge in %%post
- add postfix chroot support in init script (#5134)
- decompress all patches and sources

* Wed May 24 2006 Guillaume Rousse <guillomovitch@mandriva.org> 0.58-7mdk
- fix buildrequires
- fix initscript

* Wed May 24 2006 Guillaume Rousse <guillomovitch@mandriva.org> 0.58-6mdk
- resurect authdaemon subpackage
- mv plugins in runtime packages
- mv configuration in /etc/courier

* Wed May 17 2006 Guillaume Rousse <guillomovitch@mandriva.org> 0.58-5mdk
- conflicts with old courier-imap release (fix bug #22476)
- obsoletes plugin packages previsouly shipped with courier-imap
- fix configure invocation
- fix some perms

* Mon May 15 2006 Guillaume Rousse <guillomovitch@mandriva.org> 0.58-4mdk
- drop vpopmail support
- minor initscript corrections

* Thu May 11 2006 Guillaume Rousse <guillomovitch@mandriva.org> 0.58-3mdk
- no need for libification
- rename courier-authdaemon to courier-authlib
- don't ship .dist configuration files, and patch sysconftool to handle .rpmnew instead
- spec cleanup
- LSB-compliant init script
- simpler %%post/%%pre scripts using condrestart
- don't ship socket in package

* Thu May 11 2006 Jerome Soyer <saispo@mandriva.org> 0.58-2mdk
- Remove not needed "%%pre"

* Wed May 10 2006 Jerome Soyer <saispo@mandriva.org> 0.58-1mdk
- New release 0.58
- Use mkrel

* Thu Apr 21 2005 Oden Eriksson <oeriksson@mandriva.com> 0.55-4mdk
- rebuilt against new postgresql libs

* Sun Mar 06 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.55-3mdk
- fix some minor issues
- make it compile on 10.0 too (libtool mess)
- make it somewhat possible to link against vpopmail
- do some libifiction
- rename the initscript to courier-authdaemond

* Sat Mar 05 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.55-2mdk
- fix deps

* Fri Mar 04 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.55-1mdk
- 0.55

* Tue Mar 01 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.54-1mdk
- initial Mandrakelinux package
- added a more standard initscript (S2)
- used tiny parts of the provided spec file

