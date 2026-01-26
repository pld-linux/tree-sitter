#
# Conditional build:
%bcond_without	cli	# CLI tool for generating and testing parsers (rust-based)

%define		crates_ver	%{version}

%define		min_api_ver	13
%define		max_api_ver	15

Summary:	An incremental parsing system for programming tools
Summary(pl.UTF-8):	System przyrostowej analizy składni dla narzędzi programistycznych
Name:		tree-sitter
Version:	0.26.3
Release:	1
License:	MIT
Group:		Libraries
#Source0Download: https://github.com/tree-sitter/tree-sitter/releases
Source0:	https://github.com/tree-sitter/tree-sitter/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	8d32828a916b65e6a96c8efe68dbfd8d
# cargo vendor-filterer --platform='*-unknown-linux-*' --tier=2 --versioned-dirs && tar cJf tree-sitter-crates-VERSION.tar.xz vendor Cargo.lock
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	1c4c12869119a4346ec58ae6ff29da6b
URL:		https://tree-sitter.github.io/
BuildRequires:	rpmbuild(macros) >= 2.050
%if %{with cli}
BuildRequires:	cargo
BuildRequires:	rust >= 1.84
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
# rustc host libclang for bindgen
%ifarch x32
BuildRequires:	clang-libs(x86_64)
%else
BuildRequires:	clang-libs
%endif
%endif
%{lua:for abi=tonumber(macros.min_api_ver),tonumber(macros.max_api_ver) do
print("Provides:\tc-tree-sitter(abi)"..rpm.expand("%{?_isa}").." = "..abi.."\n")
end}
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

%description -l pl.UTF-8
Tree-sitter to narzędzie do generowania parserów oraz biblioteka do
przyrostowej analizy składni. Potrafi budować drzewa składniowe dla
plików źródłowych oraz wydajnie uaktualniać drzewo składniowe w miarę
edycji pliku źródłowego. Projekt ma być:
- wystarczająco ogólny, aby analizować dowolny język programowania
- wystarczająco szybki, aby analizować przy każdym naciśnięciu
  klawisza w edytorze
- wystarczająco funkcjonalny, aby dać przydatne wyniki nawet w
  przypadku błędów składni
- wolny od zależności, dzięki czemu biblioteka uruchomieniowa
  (napisana w czystym C) może być osadzona w dowolnej aplikacji

%package devel
Summary:	Header files for tree-sitter library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki tree-sitter
Group:		Development/Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description devel
Header files for tree-sitter library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki tree-sitter.

%package static
Summary:	Static tree-sitter library
Summary(pl.UTF-8):	Statyczna biblioteka tree-sitter
Group:		Development/Libraries
Requires:	%{name}-devel%{?_isa} = %{version}-%{release}

%description static
Static tree-sitter library.

%description static -l pl.UTF-8
Statyczna biblioteka tree-sitter.

%package cli
Summary:	tree-sitter command line utility
Summary(pl.UTF-8):	Narzędzie linii poleceń tree-sitter
Group:		Development/Tools
Requires:	%{name}%{?_isa} = %{version}-%{release}
%{?rust_req}
Requires:	gcc
Requires:	gcc-c++
Requires:	nodejs

%description cli
The Tree-sitter CLI allows you to develop, test, and use Tree-sitter
grammars from the command line.

%description cli -l pl.UTF-8
Tree-sitter CLI pozwala na rozwijanie, testowanie i używanie gramatyk
Tree-sitter z linii poleceń.

%prep
%setup -q %{?with_cli:-a1}

%if %{with cli}
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >>$CARGO_HOME/config.toml <<EOF

[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF
%endif

%build
grep -q 'TREE_SITTER_MIN_COMPATIBLE_LANGUAGE_VERSION[[:space:]]*%{min_api_ver}$' lib/include/tree_sitter/api.h
grep -q 'TREE_SITTER_LANGUAGE_VERSION[[:space:]]*%{max_api_ver}$' lib/include/tree_sitter/api.h

%{__make} \
	PREFIX="%{_prefix}" \
	INCLUDEDIR="%{_includedir}" \
	LIBDIR="%{_libdir}" \
	PCLIBDIR="%{_pkgconfigdir}" \
	CC="%{__cc}" \
	CFLAGS="%{rpmcppflags} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"

%if %{with cli}
export CARGO_HOME="$(pwd)/.cargo"
%cargo_build --frozen --package tree-sitter-cli
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
export CARGO_HOME="$(pwd)/.cargo"
%cargo_install --frozen --root $RPM_BUILD_ROOT%{_prefix} --path $PWD/crates/cli
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE README.md
%{_libdir}/libtree-sitter.so.0.26

%files devel
%defattr(644,root,root,755)
# intermediate symlink (not soname)
%{_libdir}/libtree-sitter.so.0
%{_libdir}/libtree-sitter.so
%{_includedir}/tree_sitter
%{_pkgconfigdir}/tree-sitter.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libtree-sitter.a

%if %{with cli}
%files cli
%defattr(644,root,root,755)
%doc crates/cli/{LICENSE,README.md}
%attr(755,root,root) %{_bindir}/tree-sitter
%endif
