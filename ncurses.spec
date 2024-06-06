Name:       ncurses

%define keepstatic 1
%bcond_with ncurses_abi5

Summary:    Ncurses support utilities
Version:    6.5+git1
Release:    1
License:    MIT
URL:        http://invisible-island.net/ncurses/ncurses.html
Source0:    %{name}-6.5.tar.gz
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
Requires:   %{name}-base = %{version}-%{release}

%description term
This package contains additional terminal descriptions not found in
the ncurses-base package.


%package base
Summary:    Descriptions of common terminals
Conflicts:   %{name} < 5.6-13

%description base
This package contains descriptions of common terminals. Other terminal
descriptions are included in the ncurses-term package.


%package static
Summary:    Static libraries for the ncurses library
Requires:   %{name}-devel = %{version}-%{release}

%description static
The ncurses-static package includes static libraries of the ncurses library.


%package devel
Summary:    Development files for the ncurses library
Requires:   %{name}-libs = %{version}-%{release}

%description devel
The header files and libraries for developing applications that use
the ncurses terminal handling library.

Install the ncurses-devel package if you want to develop applications
which will use ncurses.


%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}
Obsoletes: %{name}-docs

%description doc
Man pages for %{name}.

%if %{with ncurses_abi5}
%package libs5
Summary:    Ncurses libraries
Requires:   %{name}-base = %{version}-%{release}
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description libs5
The curses library routines are a terminal-independent method of
updating character screens with reasonable optimization.  The ncurses
(new curses) library is a freely distributable replacement for the
discontinued 4.4 BSD classic curses library.

This package contains the ABI version 5 of the ncurses libraries for compatibility.
%endif

%prep
%autosetup -n %{name}-6.5

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
        --with-ticlib=tic \\\
        --with-termlib=tinfo
%define abi5_options --with-chtype=long

for abi in 6 %{?with_ncurses_abi5: 5}; do
    for char in narrowc widec; do
        mkdir $char$abi
        pushd $char$abi
        ln -s %{_builddir}/%{buildsubdir}/configure .

        [ $abi = 6 ] && [ $char = widec ] && progs=yes || progs=no

        %configure $(
            echo %ncurses_options --with-abi-version=$abi
            [ $abi = 5 ] && echo %{abi5_options}
            [ $char = widec ] && echo --enable-widec || echo --disable-widec
            [ $progs = yes ] || echo --without-progs
        )
        %make_build libs
        [ $progs = yes ] && %make_build -C progs

        popd
    done
done

%install

%if %{with ncurses_abi5}
%{__make} -C narrowc5 DESTDIR=$RPM_BUILD_ROOT install.libs
rm ${RPM_BUILD_ROOT}%{_libdir}/lib{tic,tinfo}.so.5*
%{__make} -C widec5 DESTDIR=$RPM_BUILD_ROOT install.libs
rm -f $RPM_BUILD_ROOT%{_bindir}/ncurses*5-config
%endif

%{__make} -C narrowc6 DESTDIR=$RPM_BUILD_ROOT install.libs
rm -f $RPM_BUILD_ROOT%{_libdir}/lib{tic,tinfo}.so.6*
%{__make} -C widec6 DESTDIR=$RPM_BUILD_ROOT install.{libs,progs,data,includes,man}

chmod 755 ${RPM_BUILD_ROOT}%{_libdir}/lib*.so.*.*
chmod 644 ${RPM_BUILD_ROOT}%{_libdir}/lib*.a

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/terminfo

baseterms=

# prepare -base and -term file lists
for termname in \
    alacritty ansi dumb foot\* linux vt100 vt100-nav vt102 vt220 vt52 \
    Eterm\* aterm bterm cons25 cygwin eterm\* gnome gnome-256color hurd jfbterm \
    kitty konsole konsole-256color mach\* mlterm mrxvt nsterm putty{,-256color} pcansi \
    rxvt{,-\*} screen{,-\*color,.[^mlp]\*,.linux,.mlterm\*,.putty{,-256color},.mrxvt} \
    st{,-\*color} sun teraterm teraterm2.3 tmux{,-\*} vte vte-256color vwmterm \
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

%if 0
#  Avoid linker script libterminfo.so as bash/readline configure can not handle
# this. It will falsely detect libtinfo as termcap.
echo "INPUT(-ltinfo)" > $RPM_BUILD_ROOT%{_libdir}/libtermcap.so
%endif

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
%{_bindir}/[cirt]*

%files libs
%{_libdir}/lib*.so.6*

%if %{with ncurses_abi5}
%files libs5
%{_libdir}/lib*.so.5*
%endif

%files term -f terms.term

%files base -f terms.base
%license COPYING
%dir %{_sysconfdir}/terminfo
%{_datadir}/tabset
%dir %{_datadir}/terminfo

%files static
%{_libdir}/lib*.a

%files devel
%{_bindir}/ncurses*-config
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%dir %{_includedir}/ncurses
%dir %{_includedir}/ncursesw
%{_includedir}/ncurses/*.h
%{_includedir}/ncursesw/*.h
%{_includedir}/*.h

%files doc
%{_mandir}/man*/*.*
