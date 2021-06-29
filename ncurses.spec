Name:       ncurses

%define keepstatic 1

Summary:    Ncurses support utilities
Version:    6.1+git3
Release:    1
Group:      System/Base
License:    MIT
URL:        http://invisible-island.net/ncurses/ncurses.html
Source0:    %{name}-6.1.tar.gz
Source101:  ncurses-rpmlintrc
Requires:   %{name}-libs
Provides:   console-tools
Obsoletes:  ncurses < 6.1+git2

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
Requires:   %{name}-base = %{version}-%{release}
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
Requires:   %{name}-base = %{version}-%{release}

%description term
This package contains additional terminal descriptions not found in
the ncurses-base package.


%package base
Summary:    Descriptions of common terminals
Group:      System/Base
Conflicts:   %{name} < 5.6-13

%description base
This package contains descriptions of common terminals. Other terminal
descriptions are included in the ncurses-term package.


%package static
Summary:    Static libraries for the ncurses library
Group:      Development/Libraries
Requires:   %{name}-devel = %{version}-%{release}

%description static
The ncurses-static package includes static libraries of the ncurses library.


%package devel
Summary:    Development files for the ncurses library
Group:      Development/Libraries
Requires:   %{name}-libs = %{version}-%{release}

%description devel
The header files and libraries for developing applications that use
the ncurses terminal handling library.

Install the ncurses-devel package if you want to develop applications
which will use ncurses.


%package doc
Summary:   Documentation for %{name}
Group:     Documentation
Requires:  %{name} = %{version}-%{release}
Obsoletes: %{name}-docs

%description doc
Man pages for %{name}.


%prep
%setup -q -n %{name}-6.1

%build

# this will be in documentation, drop executable bits
cp -p install-sh test
chmod 644 test/*

for f in ANNOUNCE; do
iconv -f iso8859-1 -t utf8 -o ${f}{_,} &&
touch -r ${f}{,_} && mv -f ${f}{_,}
done

%define ncurses_options \\\
--with-shared --without-ada --with-ospeed=unsigned \\\
--enable-hard-tabs --enable-xmc-glitch --enable-colorfgbg \\\
--with-terminfo-dirs=%{_sysconfdir}/terminfo:%{_datadir}/terminfo \\\
--enable-overwrite \\\
--enable-pc-files \\\
--with-pkg-config-libdir=%{_libdir}/pkgconfig \\\
--with-termlib=tinfo \\\
--with-chtype=long

mkdir -p narrowc widec
cd narrowc
ln -sf ../configure .
%configure %{ncurses_options} --with-ticlib
make %{?_smp_mflags} libs
make %{?_smp_mflags} -C progs

cd ../widec
ln -sf ../configure .
%configure %{ncurses_options} --enable-widec --without-progs
make %{?_smp_mflags} libs
cd ..

%install
rm -rf %{buildroot}

make -C narrowc DESTDIR=$RPM_BUILD_ROOT install.{libs,progs,data}
rm -f $RPM_BUILD_ROOT%{_libdir}/libtinfo.*
make -C widec DESTDIR=$RPM_BUILD_ROOT install.{libs,includes,man}

chmod 755 ${RPM_BUILD_ROOT}%{_libdir}/lib*.so.*.*
chmod 644 ${RPM_BUILD_ROOT}%{_libdir}/lib*.a

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/terminfo

baseterms=

# prepare -base and -term file lists
for termname in \
ansi dumb linux vt100 vt100-nav vt102 vt220 vt52 \
Eterm\* aterm cons25 cygwin eterm\* gnome gnome-256color hurd jfbterm \
konsole konsole-256color mach\* mlterm mrxvt nsterm putty\* pcansi \
rxvt rxvt-\* screen screen-\* screen.\* sun teraterm teraterm2.3 \
wsvt25\* xfce xterm xterm-\*
do
    for i in $RPM_BUILD_ROOT%{_datadir}/terminfo/?/$termname; do
        inum=$(ls -i $i | cut -d' ' -f1)
        for t in $(find $RPM_BUILD_ROOT%{_datadir}/terminfo -inum $inum); do
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

# don't require -ltinfo when linking with --no-add-needed
for l in $RPM_BUILD_ROOT%{_libdir}/libncurses{,w}.so; do
soname=$(basename $(readlink $l))
rm -f $l
echo "INPUT($soname -ltinfo)" > $l
done

rm -f $RPM_BUILD_ROOT%{_libdir}/terminfo
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/{*_g,ncurses++*}.pc


%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%{_bindir}/[cirt]*

%files libs
%defattr(-,root,root,-)
%{_libdir}/lib*.so.*

%files term -f terms.term
%defattr(-,root,root,-)

%files base -f terms.base
%defattr(-,root,root,-)
%license COPYING
%dir %{_sysconfdir}/terminfo
%{_datadir}/tabset
%dir %{_datadir}/terminfo

%files static
%defattr(-,root,root,-)
%{_libdir}/lib*.a

%files devel
%defattr(-,root,root,-)
%{_bindir}/ncurses*-config
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%dir %{_includedir}/ncurses
%dir %{_includedir}/ncursesw
%{_includedir}/ncurses/*.h
%{_includedir}/ncursesw/*.h
%{_includedir}/*.h

%files doc
%defattr(-,root,root,-)
%{_mandir}/man*/*.*
