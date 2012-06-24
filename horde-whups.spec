
%define	_snap	2005-05-09
%define	_rel	1.1

%include	/usr/lib/rpm/macros.php
Summary:	The Web Horde User Problem Solver
Summary(pl):	Narz�dzie WWW do rozwi�zywania problem�w dla Horde
Name:		whups
Version:	1.0
Release:	%{?_snap:0.%(echo %{_snap} | tr -d -).}%{_rel}
License:	BSD
Group:		Applications/WWW
Source0:	http://ftp.horde.org/pub/snaps/%{_snap}/%{name}-HEAD-%{_snap}.tar.gz
# NoSource0-md5:	4b2f2cdd2a04e7e0ef65c9ca15f4481f
# don't put snapshots to df
NoSource:	0
Source1:	%{name}.conf
URL:		http://www.horde.org/whups/
BuildRequires:	rpmbuild(macros) >= 1.226
Requires:	apache >= 1.3.33-2
Requires:	apache(mod_access)
Requires:	horde >= 3.0
Requires:	php-mysql
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# horde accesses it directly in help->about
%define		_noautocompressdoc	CREDITS
%define		_noautoreq		'pear(Horde.*)'

%define		hordedir	/usr/share/horde
%define		_appdir		%{hordedir}/%{name}
%define		_sysconfdir	/etc/horde.org

%description
Whups is Horde's bug tracking/ticketing system. It is designed to be
extremely flexible in letting users define kinds of tickets, different
lifecycles (sets of states) and priorities for each kind of ticket,
and mixing types of tickets into sets of queues. This design allows
for very general and sophisticated multi-purpose uses of Whups. The
code is near 1.0 quality and most features are fully implemented at
this time.

%description -l pl
Whups to system �ledzienia b��d�w/zg�osze� dla Horde. Jest
zaprojektowany tak, by by� skrajnie elastycznym, pozwalaj�c
u�ytkownikom definiowa� rodzaje zg�osze�, r�ne cykle �ycia (zbiory
stan�w) i priorytety dla ka�dego rodzaju zg�oszenia, a tak�e ��czy�
rodzaje zg�osze� w zbiory kolejek. Taki spos�b zaprojektowania
pozwala na bardzo og�lne i wymy�le sposoby wykorzystania Whups do
wielu cel�w. Kod osi�gn�� prawie jako�� 1.0 i wi�kszo�� mo�liwo�ci
jest ju� w pe�ni zaimplementowana.

%prep
%setup -q -n %{name}
rm -f {lib,scripts,config,templates}/.htaccess

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name} \
	$RPM_BUILD_ROOT%{_appdir}/{docs,lib,locale,templates,themes,ticket}

cp -pR	*.php			$RPM_BUILD_ROOT%{_appdir}
for i in config/*.dist; do
	cp -p $i $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/$(basename $i .dist)
done
cp -pR	config/*.xml		$RPM_BUILD_ROOT%{_sysconfdir}/%{name}

echo "<?php ?>" > 		$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/conf.php
cp -p config/conf.xml $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/conf.xml
> $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/conf.php.bak

cp -pR lib/*			$RPM_BUILD_ROOT%{_appdir}/lib
cp -pR locale/*			$RPM_BUILD_ROOT%{_appdir}/locale
cp -pR templates/*		$RPM_BUILD_ROOT%{_appdir}/templates
cp -pR themes/*			$RPM_BUILD_ROOT%{_appdir}/themes
cp -pR ticket/*			$RPM_BUILD_ROOT%{_appdir}/ticket

ln -s %{_sysconfdir}/%{name} 	$RPM_BUILD_ROOT%{_appdir}/config
ln -s %{_defaultdocdir}/%{name}-%{version}/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs

install %{SOURCE1} 		$RPM_BUILD_ROOT%{_sysconfdir}/apache-%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/%{name}/conf.php.bak ]; then
	install /dev/null -o root -g http -m660 %{_sysconfdir}/%{name}/conf.php.bak
fi

if [ "$1" = 1 ]; then
%banner %{name} -e <<EOF
IMPORTANT:
If You are installing WHUPS for the first time, You may need to
create the database tables. Look into directory
%{_docdir}/%{name}-%{version}/scripts/sql
to find out how to do this for your database.

EOF
fi

%triggerin -- apache1 >= 1.3.33-2
%apache_config_install -v 1 -c %{_sysconfdir}/apache-%{name}.conf

%triggerun -- apache1 >= 1.3.33-2
%apache_config_uninstall -v 1

%triggerin -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/apache-%{name}.conf

%triggerun -- apache >= 2.0.0
%apache_config_uninstall -v 2

%files
%defattr(644,root,root,755)
%doc LICENSE README docs/* scripts
%attr(750,root,http) %dir %{_sysconfdir}/%{name}
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/apache-%{name}.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/%{name}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/%{name}/conf.php.bak
%attr(640,root,http) %config(noreplace) %{_sysconfdir}/%{name}/[!c]*.php
%attr(640,root,http) %{_sysconfdir}/%{name}/*.xml

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
%{_appdir}/themes
%{_appdir}/ticket
