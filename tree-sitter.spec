Summary:	An incremental parsing system for programming tools
Name:		tree-sitter
Version:	0.20.6
Release:	2
License:	MIT
Group:		Libraries
Source0:	https://github.com/tree-sitter/tree-sitter/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	4ec4fe495d90a1daa66eb637cd008c72
URL:		https://tree-sitter.github.io
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

%prep
%setup -q

%build
%{__make} \
	PREFIX="%{_prefix}" \
	INCLUDEDIR="%{_includedir}" \
	LIBDIR="%{_libdir}" \
	PCLIBDIR="%{_pkgconfigdir}" \
	CC="%{__cc}" \
	CFLAGS="%{rpmcppflags} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX="%{_prefix}" \
	INCLUDEDIR="%{_includedir}" \
	LIBDIR="%{_libdir}" \
	PCLIBDIR="%{_pkgconfigdir}"

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
