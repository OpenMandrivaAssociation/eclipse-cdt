Epoch: 1

%define gcj_support             1
%define major                   4
%define minor                   0       
%define majmin                  %{major}.%{minor}
%define micro                   1
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
Release:        %mkrel 0.1.2
License:        Eclipse Public License
Group:          Development/Java
URL:            http://www.eclipse.org/cdt
Requires:       eclipse-platform


# The following tarball was generated as follows.  Note that the optional c99 and upc parsers plus the
# optional xlc support features have been removed.
#
# mkdir -p temp && cd temp
# mkdir -p home
# rm -rf org.eclipse.cdt-releng
# cvs -d:pserver:anonymous@dev.eclipse.org:/cvsroot/tools export -r CDT_4_0_1 org.eclipse.cdt-releng/org.eclipse.cdt.releng
# cd org.eclipse.cdt-releng/org.eclipse.cdt.releng/
# sed --in-place 's/home/cvsroot/' maps/cdt.map
# sed --in-place -e'81,81i\\t\t<ant antfile="build.xml" dir="${pde.build.scripts}" target="fetch">\n\t\t\t<property name="builder" value="${basedir}/master"/>\n\t\t</ant>' build.xml
# sed --in-place -e'81,81i\\t\t<ant antfile="build.xml" dir="${pde.build.scripts}" target="fetch">\n\t\t\t<property name="builder" value="${basedir}/testing"/>\n\t\t</ant>' build.xml
# sed --in-place -e'63,63i\\t\t<ant antfile="build.xml" dir="${pde.build.scripts}" target="preBuild">\n\t\t\t<property name="builder" value="${basedir}/master"/>\n\t\t</ant>' build.xml
# sed --in-place -e'63,63i\\t\t<ant antfile="build.xml" dir="${pde.build.scripts}" target="preBuild">\n\t\t\t<property name="builder" value="${basedir}/testing"/>\n\t\t</ant>' build.xml
## Remove lpgjavaruntime jar reference
# sed --in-place -e'127,129d' build.xml
# eclipse -nosplash -Duser.home=../../home \
#   -application org.eclipse.ant.core.antRunner \
#   -buildfile build.xml -DbaseLocation=/usr/share/eclipse \
#   -Dpde.build.scripts=/usr/share/eclipse/plugins/org.eclipse.pde.build/scripts \
#   -DcdtTag=CDT_4_0_1 \
#   -DdontUnzip=true fetch
# find . -name net.*.jar -exec rm {} \;
# pushd results/features
# rm -rf *c99*
# rm -rf *upc*
# popd
# pushd results/plugins
# rm -rf *c99*
# rm -rf *upc*
# popd
# pushd results/features/org.eclipse.cdt.master
# sed --in-place -e "44,47d" feature.xml
# sed --in-place -e "24,31d" feature.xml
# popd
# cd .. && tar jcf eclipse-cdt-fetched-src-CDT_4_0_1.tar.bz2 org.eclipse.cdt.releng

Source0: %{name}-fetched-src-CDT_4_0_1.tar.bz2

Source1: http://sources.redhat.com/eclipse/autotools/eclipse-cdt-fetched-src-autotools-0_9_5.tar.gz

# The following tarball was generated thusly:
#
# mkdir temp && cd temp
# cvs -d:pserver:anonymous@dev.eclipse.org:/cvsroot/tools export -r CPPUnit_20061102 \
#   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit \
#   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit-feature
# cd org.eclipse.cdt-cppunit
# tar -czvf eclipse-cdt-cppunit-20061102.tar.gz org.eclipse.cdt.cppunit*

Source2: %{name}-cppunit-20061102.tar.gz

# Binary gif file that is currently missing from the CDT.  Since
# binary patches are not possible, the gif is included as a source file.

Source3: %{name}-target_filter.gif.gz

# Patch to add special "ForAllElements" targets to CDT sdk/customTargets.xml.
Patch1: %{name}-no-cvs2-patch
# Patch to remove tests from CDT build.xml.
Patch4: %{name}-no-tests-4.0.patch
# Patch to cppunit code to support double-clicking on file names, classes, and
# member names in the Hierarchy and Failure views such that the appropriate
# file will be opened and the appropriate line will be selected.
Patch8: %{name}-cppunit-ui.patch
# Patch to upgrade version number for cppunit feature.
Patch9: %{name}-cppunit-feature.patch
# Patch to fix default paths used by cppunit wizards to find header files and
# libraries.
Patch10: %{name}-cppunit-default-location.patch
# Patch to cppunit code to remove references to deprecated class which has
# been removed in CDT 4.0.
Patch11: %{name}-cppunit-env-tab.patch

BuildRequires: eclipse-pde
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%endif
BuildRequires:  java-rpmbuild

Requires:       gdb make gcc-c++ autoconf automake eclipse-cvs-client
Requires:       eclipse-platform >= 1:3.3.0

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
sed --in-place -e "s:linux.gtk.x86/:linux.gtk.%{eclipse_arch}/:g" build.xml
pushd sdk
sed --in-place -e "74,82d" build.properties
sed --in-place -e "s:configs=\\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd
pushd master
sed --in-place -e "74,82d" build.properties
sed --in-place -e "s:configs= \\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd
%patch4 -p0
# Following is a patch to the CDT which is missing a b/w version
# of an icon.  This patch can be removed once fixed upstream.
pushd results/plugins/org.eclipse.cdt.make.ui/icons/dtool16
tar -xzf %{SOURCE3}
popd
popd

# Autotools stuff

mkdir autotools
pushd autotools
tar -xzf %{SOURCE1}
popd

# Cppunit stuff

mkdir cppunit
pushd cppunit
tar -xzf %{SOURCE2}
%patch8 -p0
%patch9 -p0
%patch10 -p0
%patch11 -p0
popd

# Upstream CVS includes random .so files.  Let's remove them now.
# We actually remove the entire "os" directory since otherwise
# we wind up with some empty directories that we don't want.
#rm -r org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/os

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
    -DdontFetchAnything=true \
    -DskipFetch=true
popd

# Autotools has dependencies on CDT so we must add these to the SDK directory
unzip -o org.eclipse.cdt.releng/results/I.*/cdt-master-*.zip -d $SDK

# Autotools build
pushd autotools
%{java} -cp $SDK/startup.jar \
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
%{java} -cp $SDK/startup.jar \
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

unzip org.eclipse.cdt.releng/results/I.*/cdt-master-*.zip \
-d ${RPM_BUILD_ROOT}/%{eclipse_base}

# Remove testing, upc, xlc, master, and gdbjtag features and plugins
rm ${RPM_BUILD_ROOT}%{eclipse_base}/features/org.eclipse.cdt.testing*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/features/org.eclipse.cdt.master*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/features/org.eclipse.cdt.debug.gdbjtag*

# Unpack all existing feature jars
for x in ${RPM_BUILD_ROOT}/%{eclipse_base}/features/*.jar; do
  dirname=`echo $x | sed -e 's:\\(.*\\)\\.jar:\\1:g'`
  mkdir -p $dirname
  unzip $x -d $dirname
  rm $x
done 

rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.cdt.testing*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.cdt.debug.gdbjtag*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.ant*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.test*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.cdt.core.test*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.cdt.debug.ui.test*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.cdt.managedbuilder.core.test*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.cdt.managedbuilder.ui.test*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.cdt.refactoring.test*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/plugins/org.eclipse.cdt.ui.test*
rm ${RPM_BUILD_ROOT}%{eclipse_base}/site.xml
rm ${RPM_BUILD_ROOT}%{eclipse_base}/pack.properties

# We move arch-specific plugins to libdir.
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/eclipse
pushd ${RPM_BUILD_ROOT}
mkdir -p .%{_libdir}/eclipse/plugins
for archplugin in $(find .%{eclipse_base}/plugins -name \*%{eclipse_arch}_%{majmin}\*); do
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
aot-compile-rpm
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
%{eclipse_base}/plugins/org.eclipse.cdt.debug.mi*
%{eclipse_base}/plugins/org.eclipse.cdt.debug.ui*
%{eclipse_base}/plugins/org.eclipse.cdt.debug.core*
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

%files sdk
%defattr(-,root,root)
%{eclipse_base}/features/org.eclipse.cdt.sdk*
%{eclipse_base}/features/org.eclipse.cdt.source*
%{eclipse_base}/plugins/org.eclipse.cdt.source*
%{eclipse_base}/plugins/org.eclipse.cdt.sdk*
%{_libdir}/eclipse/plugins/org.eclipse.cdt.source*
