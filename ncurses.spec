# 
# Do not Edit! Generated by:
# spectacle version 0.16
# 
# >> macros
# << macros
%define keepstatic 1

Name:       ncurses
Summary:    Ncurses support utilities
Version:    5.7
Release:    3.20090207
Group:      System/Base
License:    MIT
URL:        http://invisible-island.net/ncurses/ncurses.html
Source0:    http://ftp.gnu.org/pub/gnu/ncurses/ncurses-%{version}.tar.gz
Source100:  ncurses.yaml
Source101:  ncurses-rpmlintrc
Patch0:     ncurses-5.7-20081115-20090207.patch.bz2
Patch1:     ncurses-5.7-20090124-config.patch
Patch2:     ncurses-5.6-20070612-libs.patch
Patch3:     ncurses-5.6-20080112-urxvt.patch
Patch4:     ncurses-5.6-20080628-kbs.patch
BuildRequires:  pkgconfig

%description
The curses library routines are a terminal-independent method of
updating character screens with reasonable optimization.  The ncurses
(new curses) library is a freely distributable replacement for the
discontinued 4.4 BSD classic curses library.

This package contains support utilities, including a terminfo compiler
tic, a decompiler infocmp, clear, tput, tset, and a termcap conversion
tool captoinfo.



%package libs
Summary:    Ncurses libraries
Group:      System/Libraries
Requires:   %{name} = %{version}-%{release}
Requires:   ncurses-base = %{version}-%{release}
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description libs
The curses library routines are a terminal-independent method of
updating character screens with reasonable optimization.  The ncurses
(new curses) library is a freely distributable replacement for the
discontinued 4.4 BSD classic curses library.

This package contains the ncurses libraries.


%package term
Summary:    Terminal descriptions
Group:      System/Base
Requires:   %{name} = %{version}-%{release}
Requires:   ncurses-base = %{version}-%{release}

%description term
This package contains additional terminal descriptions not found in
the ncurses-base package.


%package base
Summary:    Descriptions of common terminals
Group:      System/Base
Requires:   %{name} = %{version}-%{release}
Conflicts:   ncurses < 5.6-13

%description base
This package contains descriptions of common terminals. Other terminal
descriptions are included in the ncurses-term package.


%package static
Summary:    Static libraries for the ncurses library
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}
Requires:   ncurses-devel = %{version}-%{release}

%description static
The ncurses-static package includes static libraries of the ncurses library.

%package devel
Summary:    Development files for the ncurses library
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}
Requires:   ncurses-libs = %{version}-%{release}

%description devel
The header files and libraries for developing applications that use
the ncurses terminal handling library.

Install the ncurses-devel package if you want to develop applications
which will use ncurses.



%prep
%setup -q -n %{name}-%{version}

# ncurses-5.7-20081115-20090207.patch.bz2
%patch0 -p1
# ncurses-5.7-20090124-config.patch
%patch1 -p1
# ncurses-5.6-20070612-libs.patch
%patch2 -p1
# ncurses-5.6-20080112-urxvt.patch
%patch3 -p1
# ncurses-5.6-20080628-kbs.patch
%patch4 -p1
# >> setup
%docs_package
# << setup

%build
# >> build pre

# this will be in documentation, drop executable bits
cp -p install-sh test
chmod 644 test/*

for f in ANNOUNCE; do
iconv -f iso8859-1 -t utf8 -o ${f}{_,} &&
touch -r ${f}{,_} && mv -f ${f}{_,}
done

# << build pre

%configure 

# >> build post

%define rootdatadir /lib
%define ncurses_options \\\
--with-shared --without-ada --with-ospeed=unsigned \\\
--enable-hard-tabs --enable-xmc-glitch --enable-colorfgbg \\\
--with-terminfo-dirs=%{_sysconfdir}/terminfo:%{_datadir}/terminfo:%{rootdatadir}/terminfo \\\
--enable-overwrite \\\
--enable-pc-files \\\
--with-termlib=tinfo \\\
--with-chtype=long

export PKG_CONFIG_LIBDIR=%{_libdir}/pkgconfig

mkdir narrowc widec
cd narrowc
ln -s ../configure .
%configure %{ncurses_options} --with-ticlib
make %{?_smp_mflags} libs
make %{?_smp_mflags} -C progs

cd ../widec
ln -s ../configure .
%configure %{ncurses_options} --enable-widec --without-progs
make %{?_smp_mflags} libs
cd ..

# << build post
%install
rm -rf %{buildroot}
# >> install pre
# << install pre

# >> install post

make -C narrowc DESTDIR=$RPM_BUILD_ROOT install.{libs,progs,data}
rm -f $RPM_BUILD_ROOT%{_libdir}/libtinfo.*
make -C widec DESTDIR=$RPM_BUILD_ROOT install.{libs,includes,man}

chmod 755 ${RPM_BUILD_ROOT}%{_libdir}/lib*.so.*.*
chmod 644 ${RPM_BUILD_ROOT}%{_libdir}/lib*.a

# move lib{ncurses{,w},tinfo}.so.* to /lib*
mkdir $RPM_BUILD_ROOT/%{_lib}
mv $RPM_BUILD_ROOT%{_libdir}/lib{ncurses{,w},tinfo}.so.* $RPM_BUILD_ROOT/%{_lib}
for l in $RPM_BUILD_ROOT%{_libdir}/lib{ncurses{,w},tinfo}.so; do
ln -sf $(echo %{_libdir} | \
sed 's,\(^/\|\)[^/][^/]*,..,g')/%{_lib}/$(readlink $l) $l
done

mkdir -p $RPM_BUILD_ROOT{%{rootdatadir},%{_sysconfdir}}/terminfo

# move few basic terminfo entries to /lib
baseterms=
for termname in \
ansi dumb linux vt100 vt100-nav vt102 vt220 vt52
do
for t in $(find $RPM_BUILD_ROOT%{_datadir}/terminfo \
-samefile $RPM_BUILD_ROOT%{_datadir}/terminfo/${termname::1}/$termname)
do
baseterms="$baseterms $(basename $t)"
done
done
for termname in $baseterms; do
termpath=terminfo/${termname::1}/$termname
mkdir $RPM_BUILD_ROOT%{rootdatadir}/terminfo/${termname::1} &> /dev/null || :
mv $RPM_BUILD_ROOT%{_datadir}/$termpath $RPM_BUILD_ROOT%{rootdatadir}/$termpath
ln -s $(dirname %{_datadir}/$termpath | \
sed 's,\(^/\|\)[^/][^/]*,..,g')%{rootdatadir}/$termpath \
$RPM_BUILD_ROOT%{_datadir}/$termpath
done

# prepare -base and -term file lists
for termname in \
Eterm\* aterm cons25 cygwin eterm\* gnome gnome-256color hurd jfbterm \
konsole konsole-256color mach\* mlterm mrxvt nsterm putty\* pcansi \
rxvt rxvt-\* screen screen-\* screen.\* sun teraterm teraterm2.3 \
wsvt25\* xfce xterm xterm-\*
do
for i in $RPM_BUILD_ROOT%{_datadir}/terminfo/?/$termname; do
for t in $(find $RPM_BUILD_ROOT%{_datadir}/terminfo -samefile $i); do
baseterms="$baseterms $(basename $t)"
done
done
done 2> /dev/null
for t in $baseterms; do
echo "%dir %{_datadir}/terminfo/${t::1}"
echo %{_datadir}/terminfo/${t::1}/$t
done 2> /dev/null | sort -u > terms.base
find $RPM_BUILD_ROOT%{_datadir}/terminfo \! -type d | \
sed "s|^$RPM_BUILD_ROOT||" | while read t
do
echo "%dir $(dirname $t)"
echo $t
done 2> /dev/null | sort -u | comm -2 -3 - terms.base > terms.term

# can't replace directory with symlink (rpm bug), symlink all headers
mkdir $RPM_BUILD_ROOT%{_includedir}/ncurses{,w}
for l in $RPM_BUILD_ROOT%{_includedir}/*.h; do
ln -s ../$(basename $l) $RPM_BUILD_ROOT%{_includedir}/ncurses
ln -s ../$(basename $l) $RPM_BUILD_ROOT%{_includedir}/ncursesw
done

rm -f $RPM_BUILD_ROOT%{_libdir}/libcurses{,w}.so
echo "INPUT(-lncurses)" > $RPM_BUILD_ROOT%{_libdir}/libcurses.so
echo "INPUT(-lncursesw)" > $RPM_BUILD_ROOT%{_libdir}/libcursesw.so

echo "INPUT(-ltinfo)" > $RPM_BUILD_ROOT%{_libdir}/libtermcap.so

rm -f $RPM_BUILD_ROOT%{_libdir}/terminfo
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/{*_g,ncurses++*}.pc
# << install post







%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig













%files
%defattr(-,root,root,-)
# >> files
%{_bindir}/[cirt]*
# << files


%files libs
%defattr(-,root,root,-)
# >> files libs
/%{_lib}/lib*.so.*
%{_libdir}/lib*.so.*
# << files libs

%files term -f terms.term
%defattr(-,root,root,-)
# >> files term
# << files term

%files base -f terms.base
%defattr(-,root,root,-)
# >> files base
%dir %{_sysconfdir}/terminfo
%{rootdatadir}/terminfo
%{_datadir}/tabset
%dir %{_datadir}/terminfo
# << files base

%files static
%defattr(-,root,root,-)
# >> files static
%{_libdir}/lib*.a
# << files static

%files devel
%defattr(-,root,root,-)
# >> files devel
%{_bindir}/ncurses*-config
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%dir %{_includedir}/ncurses
%dir %{_includedir}/ncursesw
%{_includedir}/ncurses/*.h
%{_includedir}/ncursesw/*.h
%{_includedir}/*.h
# << files devel
