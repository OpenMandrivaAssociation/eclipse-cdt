Epoch: 1

%define gcj_support             1
%define major                   3
%define minor                   1       
%define majmin                  %{major}.%{minor}
%define micro                   2
%define eclipse_base            %{_datadir}/eclipse
%define eclipse_lib_base        %{_libdir}/eclipse

# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%define eclipse_arch   %{_arch}
%endif

Summary:        Eclipse C/C++ Development Tools (CDT) plugin
Name:           eclipse-cdt
Version:        %{majmin}.%{micro}
Release:        %mkrel 2.2
License:        EPL
Group:          Development/Java
URL:            http://www.eclipse.org/cdt
Requires:       eclipse-platform

# The following tarball was generated like this:
#
# mkdir temp && cd temp
# mkdir home
# cvs -d:pserver:anonymous@dev.eclipse.org:/cvsroot/tools export -r CDT_3_1_2 \
#   org.eclipse.cdt-releng/org.eclipse.cdt.releng
# cd org.eclipse.cdt-releng/org.eclipse.cdt.releng/
# sed --in-place 's/@cdtTag@/CDT_3_1_2/' maps/cdt.map
# sed --in-place 's/home/cvsroot/' maps/cdt.map
# eclipse -nosplash -Duser.home=../../home \
#   -application org.eclipse.ant.core.antRunner \
#   -buildfile build.xml -DbaseLocation=/usr/share/eclipse \
#   -Dpde.build.scripts=/usr/share/eclipse/plugins/org.eclipse.pde.build/scripts \
#   -DdontUnzip=true fetch
# cd .. && tar jcf eclipse-cdt-fetched-src-3.1.2.tar.bz2 org.eclipse.cdt.releng

Source0: %{name}-fetched-src-%{version}.tar.bz2

Source1: http://sources.redhat.com/eclipse/autotools/eclipse-cdt-autotools-0.0.8.1.tar.gz

# The following tarball was generated thusly:
#
# mkdir temp && cd temp
# cvs -d:pserver:anonymous@dev.eclipse.org:/cvsroot/tools export -r CPPUnit_20061102 \
#   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit \
#   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit-feature
# cd org.eclipse.cdt-cppunit
# tar -czvf eclipse-cdt-cppunit-20061102.tar.gz org.eclipse.cdt.cppunit*

Source2: %{name}-cppunit-20061102.tar.gz

# Patch to add special "ForAllElements" targets to CDT sdk/customTargets.xml.
Patch1: %{name}-no-cvs2-patch
# Patch to remove tests from CDT build.xml.
Patch4: %{name}-no-tests.patch
# Patch to CDT to add the ability to specify a build subconsole.  The additional
# build console is # used by Autotools to display configuration output.
Patch5: %{name}-buildconsole.patch
# Patch to add new IScannerInfoPlus interface to CDT and add code to recognize it
# when opening header files via clicking on them in the outline view.  This
# stops multiple include paths from being shown when the true path is already
# known by calculation from the build's Makefile.
Patch6: %{name}-scannerinfoplus.patch
# Patch to CDT to add hover help for compiler defined symbols (i.e. -D flags).
Patch7: %{name}-definedsymbolhover.patch
# Patch to cppunit code to support double-clicking on file names, classes, and
# member names in the Hierarchy and Failure views such that the appropriate
# file will be opened and the appropriate line will be selected.
Patch8: %{name}-cppunit-ui.patch
# Patch to upgrade version number for cppunit feature.
Patch9: %{name}-cppunit-feature.patch
# Patch to fix default paths used by cppunit wizards to find header files and
# libraries.
Patch10: %{name}-cppunit-default-location.patch
# Patch to ManagedMake builder to prevent running make after Makefile generation
# failure.
Patch11: %{name}-managedbuild-failcheck.patch
Patch12: %{name}-autotools-char.patch
BuildRequires: eclipse-pde
%if %{gcj_support}
BuildRequires:  gcc-java >= 4.0.2
BuildRequires:  java-gcj-compat-devel >= 1.0.64
Requires(post):   java-gcj-compat >= 1.0.64
Requires(postun): java-gcj-compat >= 1.0.64
%else
BuildRequires:  java-devel >= 1.4.2
%endif

Requires:       gdb make gcc-c++ autoconf automake
Requires:       eclipse-platform >= 1:3.2.0

# Currently, upstream CDT only supports building on the platforms listed here.
%if %{gcj_support}
ExclusiveArch: %{ix86} x86_64 ppc ia64
%else
ExclusiveArch: %{ix86} x86_64 ppc ia64
%endif
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root

%package sdk
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Group:          Development/Java
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description
The eclipse-cdt package contains Eclipse features and plugins that are
useful for C and C++ development.

%description sdk
Source for Eclipse CDT for use within Eclipse.

%prep
%setup -q -c 
pushd "org.eclipse.cdt.releng"
%patch1 -p0
# Only build the sdk
offset=0; 
for line in $(grep -no "value=.*platform" build.xml); do
  linenum=$(echo "$line" | cut -d : -f 1)
  sed --in-place -e "$(expr $linenum - 1 - $offset ),$(expr $linenum + 1 - $offset)d" build.xml 
  offset=$(expr $offset + 3) 
done
# Only build for the platform on which we're building
pushd sdk
sed --in-place -e "74,82d" build.properties
sed --in-place -e "s:configs=\\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd
%patch4 -p0
%patch5 -p0
%patch6 -p0
%patch7 -p0
%patch11 -p0
popd

# Autotools stuff

mkdir autotools
pushd autotools
tar -xzf %{SOURCE1}
%patch12 -p0
popd

# Cppunit stuff

mkdir cppunit
pushd cppunit
tar -xzf %{SOURCE2}
%patch8 -p0
%patch9 -p0
%patch10 -p0
popd

# Upstream CVS includes random .so files.  Let's remove them now.
# We actually remove the entire "os" directory since otherwise
# we wind up with some empty directories that we don't want.
#rm -r org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/os

%{_bindir}/find . -type f -name '*.c' -o -name '*.h' | \
  %{_bindir}/xargs -t %{__perl} -pi -e 's/\r$//g'

%build
export JAVA_HOME=%{java_home}
export PATH=%{java_bin}:/usr/bin:$PATH

# See comments in the script to understand this.
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK %{eclipse_base}
SDK=$(cd SDK >/dev/null && pwd)

# Eclipse may try to write to the home directory.
mkdir home

homedir=$(cd home > /dev/null && pwd)

pushd org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/library
make JAVA_HOME="%{java_home}" ARCH=%{eclipse_arch} CC='gcc -D_GNU_SOURCE'
popd

# Call eclipse headless to process CDT releng build scripts
pushd org.eclipse.cdt.releng 
%{java} -cp $SDK/startup.jar \
    -Dosgi.sharedConfiguration.area=%{_libdir}/eclipse/configuration                        \
    -Duser.home=$homedir                        \
     org.eclipse.core.launcher.Main             \
    -application org.eclipse.ant.core.antRunner \
    -DjavacFailOnError=true \
    -DdontUnzip=true \
    -DbaseLocation=$SDK \
    -Dpde.build.scripts=%{eclipse_base}/plugins/org.eclipse.pde.build/scripts \
    -DdontFetchAnything=true
popd

# Autotools has dependencies on CDT so we must add these to the SDK directory
tar -C $SDK --strip-components=1 -zxvf org.eclipse.cdt.releng/results/I.*/org.eclipse.cdt.sdk-*.tar.gz

# Autotools build
pushd autotools
java -cp $SDK/startup.jar \
     -Dosgi.sharedConfiguration.area=%{_libdir}/eclipse/configuration                        \
     -Duser.home=$homedir                        \
     org.eclipse.core.launcher.Main             \
     -application org.eclipse.ant.core.antRunner       \
     -Dtype=feature                                    \
     -Did=com.redhat.eclipse.cdt.autotools.feature         \
     -DsourceDirectory=$(pwd)                          \
     -DbaseLocation=$SDK                               \
     -Dbuilder=%{eclipse_base}/plugins/org.eclipse.pde.build/templates/package-build  \
     -f %{eclipse_base}/plugins/org.eclipse.pde.build/scripts/build.xml 

popd

# Cppunit build
pushd cppunit
java -cp $SDK/startup.jar \
     -Dosgi.sharedConfiguration.area=%{_libdir}/eclipse/configuration                        \
     -Duser.home=$homedir                        \
     org.eclipse.core.launcher.Main             \
     -application org.eclipse.ant.core.antRunner       \
     -Dtype=feature                                    \
     -Did=org.eclipse.cdt.cppunit                      \
     -DsourceDirectory=$(pwd)                          \
     -DbaseLocation=$SDK                               \
     -Dbuilder=%{eclipse_base}/plugins/org.eclipse.pde.build/templates/package-build  \
     -f %{eclipse_base}/plugins/org.eclipse.pde.build/scripts/build.xml

popd
%install
rm -rf ${RPM_BUILD_ROOT}

install -d -m755 ${RPM_BUILD_ROOT}/%{eclipse_base}

tar -C ${RPM_BUILD_ROOT}/%{eclipse_base} --strip-components=1 -zxvf \
  org.eclipse.cdt.releng/results/I.*/org.eclipse.cdt.sdk-*.tar.gz

# We move arch-specific plugins to libdir.
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/eclipse
pushd ${RPM_BUILD_ROOT}
mkdir -p .%{_libdir}/eclipse/plugins
for archplugin in $(find .%{eclipse_base}/plugins -name \*%{eclipse_arch}_%{version}\*); do
  mv $archplugin .%{_libdir}/eclipse/plugins
  chmod -R 755 .%{_libdir}/eclipse/plugins/$(basename $archplugin)
done
popd

# These are in the SDK packages
rm ${RPM_BUILD_ROOT}%{eclipse_base}/epl-v10.html
rm ${RPM_BUILD_ROOT}%{eclipse_base}/notice.html

# Autotools install
pushd autotools
unzip -qq -d $RPM_BUILD_ROOT%{eclipse_base}/.. build/rpmBuild/com.redhat.eclipse.cdt.autotools.feature.zip
popd

# Cppunit install
pushd cppunit
unzip -qq -d $RPM_BUILD_ROOT%{eclipse_base}/.. build/rpmBuild/org.eclipse.cdt.cppunit.zip
popd

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean 
rm -rf ${RPM_BUILD_ROOT}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root)
%{eclipse_base}/features/org.eclipse.cdt_*
%{eclipse_base}/features/com.redhat.eclipse.cdt*
%{eclipse_base}/features/org.eclipse.cdt.cppunit_*
%{eclipse_base}/plugins/org.eclipse.cdt_*
%{eclipse_base}/plugins/org.eclipse.cdt.core*
%{eclipse_base}/plugins/org.eclipse.cdt.cppunit*
%{eclipse_base}/plugins/org.eclipse.cdt.debug*
%{eclipse_base}/plugins/org.eclipse.cdt.doc*
%{eclipse_base}/plugins/org.eclipse.cdt.launch*
%{eclipse_base}/plugins/org.eclipse.cdt.make*
%{eclipse_base}/plugins/org.eclipse.cdt.managedbuilder*
%{eclipse_base}/plugins/org.eclipse.cdt.refactoring*
%{eclipse_base}/plugins/org.eclipse.cdt.ui*
%{eclipse_base}/plugins/com.redhat.eclipse.cdt*
%{_libdir}/eclipse/plugins/org.eclipse.cdt.core*
%if %{gcj_support}
%{_libdir}/gcj/%{name}
%endif
%doc %{eclipse_base}/features/org.eclipse.cdt.cppunit_*/cpl-v10.html
%doc %{eclipse_base}/features/org.eclipse.cdt_*/epl-v10.html

%files sdk
%defattr(-,root,root)
%{eclipse_base}/features/org.eclipse.cdt.sdk*
%{eclipse_base}/features/org.eclipse.cdt.source*
%{eclipse_base}/plugins/org.eclipse.cdt.source*
%{eclipse_base}/plugins/org.eclipse.cdt.sdk*
%{_libdir}/eclipse/plugins/org.eclipse.cdt.source*
%doc %{eclipse_base}/features/org.eclipse.cdt.sdk_*/epl-v10.html


