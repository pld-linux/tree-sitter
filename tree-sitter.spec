#
# Conditional build:
%bcond_without	cli		# don't build cli tool for generating and testing parsers

%define		crates_ver	0.20.7

Summary:	An incremental parsing system for programming tools
Name:		tree-sitter
Version:	0.20.7
Release:	1
License:	MIT
Group:		Libraries
Source0:	https://github.com/tree-sitter/tree-sitter/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	f8fddc6c47ae32c13a6a774b1060a068
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	6a9d6656c53a88badbe754064a91f8b8
URL:		https://tree-sitter.github.io
BuildRequires:	rpmbuild(macros) >= 2.004
%if %{with cli}
BuildRequires:	cargo
BuildRequires:	rust
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Tree-sitter is a parser generator tool and an incremental parsing
library. It can build a concrete syntax tree for a source file and
efficiently update the syntax tree as the source file is edited.
Tree-sitter aims to be:
- General enough to parse any programming language
- Fast enough to parse on every keystroke in a text editor
- Robust enough to provide useful results even in the presence of
  syntax errors
- Dependency-free so that the runtime library (which is written in
  pure C) can be embedded in any application

%package devel
Summary:	Header files for tree-sitter library
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for tree-sitter library.

%package static
Summary:	Static tree-sitter library
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static tree-sitter library.

%package cli
Summary:	tree-sitter command line utility
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	gcc
Requires:	gcc-c++
Requires:	nodejs

%description cli
The Tree-sitter CLI allows you to develop, test, and use Tree-sitter
grammars from the command line.

%prep
%setup -q %{?with_cli:-a1}

%if %{with cli}
%{__mv} -f tree-sitter-%{crates_ver}/cli/vendor/* cli/vendor

export CARGO_HOME="$(pwd)/cli/.cargo"

mkdir -p "$CARGO_HOME"
cat >$CARGO_HOME/config <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/cli/vendor'
EOF
%endif

%build
%{__make} \
	PREFIX="%{_prefix}" \
	INCLUDEDIR="%{_includedir}" \
	LIBDIR="%{_libdir}" \
	PCLIBDIR="%{_pkgconfigdir}" \
	CC="%{__cc}" \
	CFLAGS="%{rpmcppflags} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"

%if %{with cli}
export CARGO_HOME="$(pwd)/cli/.cargo"
cd cli
%cargo_build --frozen
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX="%{_prefix}" \
	INCLUDEDIR="%{_includedir}" \
	LIBDIR="%{_libdir}" \
	PCLIBDIR="%{_pkgconfigdir}"

%if %{with cli}
export CARGO_HOME="$(pwd)/cli/.cargo"
cd cli
%cargo_install --frozen --root $RPM_BUILD_ROOT%{_prefix} --path $PWD
cd ..
%{__rm} $RPM_BUILD_ROOT%{_prefix}/.crates*
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc CONTRIBUTING.md README.md
%attr(755,root,root) %{_libdir}/libtree-sitter.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libtree-sitter.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libtree-sitter.so
%{_includedir}/tree_sitter
%{_pkgconfigdir}/tree-sitter.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libtree-sitter.a

%if %{with cli}
%files cli
%defattr(644,root,root,755)
%doc cli/README.md
%attr(755,root,root) %{_bindir}/tree-sitter
%endif
