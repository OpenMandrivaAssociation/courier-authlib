Name:		courier-authlib
Version:	0.73.2
Release:	2
Summary:	Courier authentication library
Group:		System/Servers
License:	GPL
URL:		https://www.courier-mta.org
Source0:	http://prdownloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2
Source1:	courier-authlib.sysconftool.m4
Source2:	courier-authlib.authdaemon-init
Patch0:		courier-authlib-0.65.sysconftool.patch
Patch1:		courier-authlib-0.73.2-tcpremoteip.patch
BuildRequires:	autoconf
BuildRequires:	autoconf-archive
BuildRequires:	automake
BuildRequires:	libtool-base
BuildRequires:	slibtool
BuildRequires:	make
BuildRequires:	expect
BuildRequires:	libltdl-devel
BuildRequires:	gdbm-devel
BuildRequires:	pkgconfig(sqlite3)
# 0.73 requires the Courier Unicode library 2.6
BuildRequires:	%mklibname courier-unicode -d
BuildRequires:	pkgconfig(ldap)
BuildRequires:	pam-devel
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	pkgconfig(libidn2)
BuildRequires:	procps-ng
# iconv loads ISO-8859-1 from this package. The rfc822 test decodes it.
BuildRequires:	locales-extra-charsets
Requires:	procps-ng
Requires:	locales-extra-charsets
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
%patch 0 -p0 -b .sysconftool
%patch 1 -p1

# The configure step reruns aclocal and ignores *.m4 files in the top directory.
mkdir -p m4
cp %{SOURCE1} m4/sysconftool.m4

# slibtoolize installs a stub ltmain.sh. aclocal has to see slibtool's
# macros, or the generated libtool script exits before it links.
find . -name configure.ac | while read f; do
	d=$(dirname "$f")
	if grep -qE 'LT_INIT|LIBTOOL' "$f"; then
		mkdir -p "$d/m4"
		cp -a /usr/share/slibtool/slibtool.m4 "$d/m4/"
		cp -a /usr/share/slibtool/sltdl.m4 "$d/m4/"
	fi
done

%build
export slibtool_prefer_sltdl=no
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
# Subdirectory rebuilds update m4 files that the top configure depends on.
# Make would then rerun aclocal without the m4 include path.
find . \( -name configure -o -name aclocal.m4 -o -name Makefile.in -o -name '*.h.in' \) -exec touch {} +
find . \( -name config.status -o -name stamp-h -o -name stamp-h1 \) -exec touch {} +
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

install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/courier-authdaemon
mv %{buildroot}%{_libexecdir}/courier-authlib/authdaemond %{buildroot}%{_sbindir}/authdaemond
# The install hook copies the libtool wrapper. Ship the linked binary.
rm -f %{buildroot}%{_libexecdir}/courier-authlib/makedatprog
install -m 755 libs/makedat/.libs/makedatprog %{buildroot}%{_sbindir}/makedatprog
install -m 755 userdb/.libs/userdbpw %{buildroot}%{_sbindir}/userdbpw

# some utils...
install -m 755 authinfo %{buildroot}%{_sbindir}/
install -m 755 .libs/authdaemontest %{buildroot}%{_sbindir}/
install -m 755 libs/liblock/.libs/lockmail %{buildroot}%{_sbindir}/
install -m 644 libs/liblock/lockmail.1 %{buildroot}%{_mandir}/man1/

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
if [ -f %{_sysconfdir}/courier/authldaprc.rpmnew ]; then
    %{_libdir}/courier-authlib/sysconftool %{_sysconfdir}/courier/authldaprc.rpmnew >/dev/null
fi
%{_initrddir}/courier-authdaemon condrestart 1>&2;
    
%postun ldap
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%post mysql
if [ -f %{_sysconfdir}/courier/authmysqlrc.rpmnew ]; then
    %{_libdir}/courier-authlib/sysconftool %{_sysconfdir}/courier/authmysqlrc.rpmnew >/dev/null
fi
%{_initrddir}/courier-authdaemon condrestart 1>&2;
    
%postun mysql
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%post pgsql
%{_initrddir}/courier-authdaemon condrestart 1>&2;
    
%postun pgsql
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%post sqlite
%{_initrddir}/courier-authdaemon condrestart 1>&2;
    
%postun sqlite
if [ "$1" = "0" ]; then
    %{_initrddir}/courier-authdaemon condrestart 1>&2;
fi

%files
%defattr(-,root,root)
%doc README.mdv README README.authdebug.html README.html README_authlib.html
%doc NEWS COPYING* AUTHORS ChangeLog libs/liblock/lockmail.html liblog/courierlogger.html
%dir %{_sysconfdir}/courier
%dir %{_libdir}/courier-authlib
%dir %{_libexecdir}/courier-authlib
%{_libexecdir}/courier-authlib/authsystem.passwd
%{_libdir}/courier-authlib/sysconftool
%{_libdir}/courier-authlib/libcourierauthsaslclient.so.*
%{_libdir}/courier-authlib/libcourierauthsasl.so.*
%{_libdir}/courier-authlib/libcourierauthcommon.so.*
%{_libdir}/courier-authlib/libcourierauth.so.*
%{_libdir}/courier-authlib/libauthcustom.so.*
%{_libdir}/courier-authlib/libauthpam.so.*
%{_libdir}/courier-authlib/libauthpwd.so.*
%{_libdir}/courier-authlib/libauthshadow.so.*
%{_libdir}/courier-authlib/libauthpipe.so.*
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
%{_sbindir}/userdbpw
%{_libdir}/courier-authlib/libauthuserdb.so.*
%{_mandir}/man8/*userdb*

%files ldap
%defattr(-,root,root)
%doc README.ldap
%config(noreplace) %{_sysconfdir}/courier/authldaprc
%{_libdir}/courier-authlib/libauthldap.so.*

%files mysql
%defattr(-,root,root)
%doc README.authmysql.html README.authmysql.myownquery
%config(noreplace) %{_sysconfdir}/courier/authmysqlrc
%{_libdir}/courier-authlib/libauthmysql.so.*

%files pgsql
%defattr(-,root,root)
%doc README.authpostgres.html
%config(noreplace) %{_sysconfdir}/courier/authpgsqlrc
%{_libdir}/courier-authlib/libauthpgsql.so.*

%files sqlite
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/courier/authsqliterc
%{_libdir}/courier-authlib/libauthsqlite.so.*

%files devel
%defattr(-,root,root)
%doc authlib.html auth_*.html
%{_bindir}/courierauthconfig
%{_libdir}/courier-authlib/*.so
%{_libdir}/*.so
%{_includedir}/*
%{_mandir}/man3/*
