%define	_hordeapp whups
%define	_snap	2006-01-08
#define	_rc		rc1
%define	_rel	0.1
#
%include	/usr/lib/rpm/macros.php
Summary:	The Web Horde User Problem Solver
Summary(pl):	Narzêdzie WWW do rozwi±zywania problemów dla Horde
Name:		horde-%{_hordeapp}
Version:	1.0
Release:	%{?_rc:0.%{_rc}.}%{?_snap:0.%(echo %{_snap} | tr -d -).}%{_rel}
License:	BSD
Group:		Applications/WWW
Source0:	ftp://ftp.horde.org/pub/snaps/%{_snap}/%{_hordeapp}-HEAD-%{_snap}.tar.gz
# Source0-md5:	7cb82901f8788c4aa1686b309a99fee1
Source1:	%{_hordeapp}.conf
URL:		http://www.horde.org/whups/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	tar >= 1:1.15.1
Requires:	horde >= 3.0
Requires:	php-mysql
Requires:	webapps
Obsoletes:	%{_hordeapp}
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# horde accesses it directly in help->about
%define		_noautocompressdoc	CREDITS
%define		_noautoreq	'pear(Horde.*)' 'pear(Text/Flowed.php)'

%define		hordedir	/usr/share/horde
%define		_appdir		%{hordedir}/%{_hordeapp}
%define		_webapps	/etc/webapps
%define		_webapp		horde-%{_hordeapp}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%description
Whups is Horde's bug tracking/ticketing system. It is designed to be
extremely flexible in letting users define kinds of tickets, different
lifecycles (sets of states) and priorities for each kind of ticket,
and mixing types of tickets into sets of queues. This design allows
for very general and sophisticated multi-purpose uses of Whups. The
code is near 1.0 quality and most features are fully implemented at
this time.

%description -l pl
Whups to system ¶ledzienia b³êdów/zg³oszeñ dla Horde. Jest
zaprojektowany tak, by byæ skrajnie elastycznym, pozwalaj±c
u¿ytkownikom definiowaæ rodzaje zg³oszeñ, ró¿ne cykle ¿ycia (zbiory
stanów) i priorytety dla ka¿dego rodzaju zg³oszenia, a tak¿e ³±czyæ
rodzaje zg³oszeñ w zbiory kolejek. Taki sposób zaprojektowania pozwala
na bardzo ogólne i wymy¶le sposoby wykorzystania Whups do wielu celów.
Kod osi±gn±³ prawie jako¶æ 1.0 i wiêkszo¶æ mo¿liwo¶ci jest ju¿ w pe³ni
zaimplementowana.

%prep
%setup -qcT -n %{?_snap:%{_hordeapp}-%{_snap}}%{!?_snap:%{_hordeapp}-%{version}%{?_rc:-%{_rc}}}
tar zxf %{SOURCE0} --strip-components=1

rm -f {,*/}.htaccess
for i in config/*.dist; do
	mv $i config/$(basename $i .dist)
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}/docs}

cp -a *.php $RPM_BUILD_ROOT%{_appdir}
cp -a config/* $RPM_BUILD_ROOT%{_sysconfdir}
echo '<?php ?>' > $RPM_BUILD_ROOT%{_sysconfdir}/conf.php
touch $RPM_BUILD_ROOT%{_sysconfdir}/conf.php.bak
cp -a lib locale templates themes ticket $RPM_BUILD_ROOT%{_appdir}

ln -s %{_sysconfdir} $RPM_BUILD_ROOT%{_appdir}/config
ln -s %{_docdir}/%{name}-%{version}/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/conf.php.bak ]; then
	install /dev/null -o root -g http -m660 %{_sysconfdir}/conf.php.bak
fi

if [ "$1" = 1 ]; then
%banner %{name} -e <<EOF
IMPORTANT:
If You are installing Whups for the first time, You may need to
create the database tables. Look into directory
%{_docdir}/%{name}-%{version}/scripts/sql
to find out how to do this for your database.

EOF
fi

%triggerin -- apache1
%webapp_register apache %{_webapp}

%triggerun -- apache1
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- horde-%{_hordeapp} < 1.0-0.20050917.0.3, %{_hordeapp}
for i in conf.php menu.php mime_drivers.php prefs.php reminders.php templates.php; do
	if [ -f /etc/horde.org/%{_hordeapp}/$i.rpmsave ]; then
		mv -f %{_sysconfdir}/$i{,.rpmnew}
		mv -f /etc/horde.org/%{_hordeapp}/$i.rpmsave %{_sysconfdir}/$i
	fi
done

if [ -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave ]; then
	mv -f %{_sysconfdir}/apache.conf{,.rpmnew}
	mv -f %{_sysconfdir}/httpd.conf{,.rpmnew}
	cp -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave %{_sysconfdir}/apache.conf
	cp -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave %{_sysconfdir}/httpd.conf
fi

if [ -L /etc/apache/conf.d/99_horde-%{_hordeapp}.conf ]; then
	/usr/sbin/webapp register apache %{_webapp}
	rm -f /etc/apache/conf.d/99_horde-%{_hordeapp}.conf
	%service -q apache reload
fi
if [ -L /etc/httpd/httpd.conf/99_horde-%{_hordeapp}.conf ]; then
	/usr/sbin/webapp register httpd %{_webapp}
	rm -f /etc/httpd/httpd.conf/99_horde-%{_hordeapp}.conf
	%service -q httpd reload
fi

%files
%defattr(644,root,root,755)
%doc LICENSE README docs/* scripts
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/conf.php.bak
%attr(640,root,http) %config(noreplace) %{_sysconfdir}/[!c]*.php
%attr(640,root,http) %{_sysconfdir}/conf.xml

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
%{_appdir}/themes
%{_appdir}/ticket
