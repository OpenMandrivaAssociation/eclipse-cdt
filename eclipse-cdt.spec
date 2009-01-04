Epoch: 1

%define gcj_support             0
%define run_tests               1
%define ship_tests              0
%define major                   5
%define minor                   0
%define majmin                  %{major}.%{minor}
%define micro                   1
%define eclipse_base            %{_libdir}/eclipse
%define build_id		200809190802

# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%define eclipse_arch   %{_arch}
%endif

Summary:        Eclipse C/C++ Development Tools (CDT) plugin
Name:           eclipse-cdt
Version:        %{majmin}.%{micro}
Release:        %mkrel 0.6.1
License:        Eclipse Public License
Group:          Development/C
URL:            http://www.eclipse.org/cdt
Requires:       eclipse-platform


# The following tarball was generated using the included fetch-cdt.sh
# script.  Note that the optional c99 and upc parsers plus the optional
# xlc support features have been removed.

Source0: %{name}-fetched-src-CDT_5_0_1.tar.bz2
Source4: fetch-cdt.sh

Source1: http://sources.redhat.com/eclipse/autotools/eclipse-cdt-fetched-src-autotools-1_0_0.tar.gz
#Source1: http://sources.redhat.com/eclipse/autotools/eclipse-cdt-fetched-src-autotools-20081106.tar.gz
#
#Source2: http://sources.redhat.com/eclipse/autotools/eclipse-cdt-fetched-src-libhover-20081106.tar.gz


## The following tarball was generated thusly:
##
## mkdir temp && cd temp
## cvs -d:pserver:anonymous@dev.eclipse.org:/cvsroot/tools export -r CPPUnit_20061102 \
##   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit \
##   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit-feature
## cd org.eclipse.cdt-cppunit
## tar -czvf eclipse-cdt-cppunit-20061102.tar.gz org.eclipse.cdt.cppunit*
#
#Source2: %{name}-cppunit-20061102.tar.gz


# Binary gif file that is currently missing from the CDT.  Since
# binary patches are not possible, the gif is included as a source file.
Source3: %{name}-target_filter.gif.gz

# Script to run the tests in Xvnc
Source5: %{name}-runtests.sh

# Don't run the tests as part of the build.  We'll do this ourselves.
Patch4: %{name}-no-tests-%{version}.patch

# Fix autotools plugin to reference correct project nature.
Patch5: %{name}-autotools-plugin.patch

# Fix for autotools property settings problem.
Patch6: %{name}-autotools-bug461647.patch

## Patch to cppunit code to support double-clicking on file names, classes, and
## member names in the Hierarchy and Failure views such that the appropriate
## file will be opened and the appropriate line will be selected.
#Patch8: %{name}-cppunit-ui.patch
## Patch to upgrade version number for cppunit feature.
#Patch9: %{name}-cppunit-feature.patch
## Patch to fix default paths used by cppunit wizards to find header files and
## libraries.
#Patch10: %{name}-cppunit-default-location.patch
## Patch to cppunit code to remove references to deprecated class which has
## been removed in CDT 4.0.
#Patch11: %{name}-cppunit-env-tab.patch

# Remove include of stropts.h in openpty.c as it is no longer included
# in glibc-headers package
Patch12: %{name}-openpty.patch

# Add XML -> HTML generation after running tests
Patch13: %{name}-testaggregation.patch

# FIXME:  investigate for 5.0.1
#
# There is a bug in this test that makes it not build.  It looks like
# it's fixed upstream in 5.0.1
# https://bugs.eclipse.org/bugs/show_bug.cgi?id=130235
Patch14: %{name}-noLexerTests.patch

BuildRequires: eclipse-pde
BuildRequires: eclipse-mylyn >= 3.0
BuildRequires: tomcat5-jsp-2.0-api
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%endif
%if %{run_tests}
BuildRequires:  vnc-server
BuildRequires:  w3m
%endif
BuildRequires:  java-rpmbuild
BuildRequires:  zip

Requires:       gdb make gcc-c++ autoconf automake
Requires:       eclipse-platform >= 1:3.4.0

# Currently, upstream CDT only supports building on the platforms listed here.
%if %{gcj_support}
ExclusiveArch: %{ix86} x86_64 ppc ia64
%else
ExclusiveArch: %{ix86} x86_64 ppc ia64
%endif
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Eclipse features and plugins that are useful for C and C++ development.

%package mylyn
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Group:          Development/Java
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       eclipse-mylyn >= 3.0

%description mylyn
Mylyn integration for CDT.

%package sdk
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Group:          Development/Java
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description sdk
Source for Eclipse CDT for use within Eclipse.

%if %{ship_tests}
%package tests
Summary:        Test suite for Eclipse C/C++ Development Tools (CDT)
Group:          Text Editors/Integrated Development Environments (IDE)
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       vnc-server

%description tests
Test suite for Eclipse C/C++ Development Tools (CDT).
%endif

%prep
%setup -q -c

%patch4

pushd "org.eclipse.cdt.releng"
# Remove lpg-using lrparser feature
sed -i "36,39d" results/features/org.eclipse.cdt.master/feature.xml

# Remove lrparser plugin
rm -rf results/plugins/org.eclipse.cdt.core.lrparser

# Following patches a C file to remove reference to stropts.h which is
# not needed and is missing in latest glibc
pushd results/plugins/org.eclipse.cdt.core.linux/library
%patch12 -p0
popd
pushd results/plugins
%patch13
popd
pushd results/plugins/org.eclipse.cdt.core.tests
rm parser/org/eclipse/cdt/core/parser/tests/scanner/LexerTests.java
%patch14
popd

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
pushd platform
sed --in-place -e "74,82d" build.properties
sed --in-place -e "s:configs=.*\\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd
# Following is a patch to the CDT which is missing a b/w version
# of an icon.  This patch can be removed once fixed upstream.
pushd results/plugins/org.eclipse.cdt.make.ui/icons/dtool16
tar -xzf %{SOURCE3}
popd

popd

## Autotools stuff

mkdir autotools
pushd autotools
tar -xzf %{SOURCE1}
pushd com.redhat.eclipse.cdt.autotools
%patch5
%patch6
popd
popd

## Libhover stuff
#mkdir libhover
#pushd libhover
#tar -xzf %{SOURCE2}
#popd

## Cppunit stuff
#
#mkdir cppunit
#pushd cppunit
#tar -xzf %{SOURCE2}
#%patch8 -p0
#%patch9 -p0
#%patch10 -p0
#%patch11 -p0
#popd

# Upstream CVS includes random .so files.  Let's remove them now.
# We actually remove the entire "os" directory since otherwise
# we wind up with some empty directories that we don't want.
#rm -r org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/os
mv org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.so \
  org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.BAK
find -name \*.so | xargs rm -rf
mv org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.BAK \
  org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.so

%build
export JAVA_HOME=%{java_home}
export PATH=%{java_bin}:/usr/bin:$PATH

# See comments in the script to understand this.
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK  \
  %{eclipse_base} mylyn xmlrpc codec httpclient lang

SDK=$(cd SDK >/dev/null && pwd)

# Eclipse may try to write to the home directory.
mkdir home

homedir=$(cd home > /dev/null && pwd)

pushd org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/library
make JAVA_HOME="%{java_home}" ARCH=%{eclipse_arch} CC='gcc -D_GNU_SOURCE'
popd

PDEBUILDVERSION=$(ls %{eclipse_base}/dropins/sdk/plugins \
  | grep org.eclipse.pde.build_ | \
  sed 's/org.eclipse.pde.build_//')
PDEDIR=%{eclipse_base}/dropins/sdk/plugins/org.eclipse.pde.build_$PDEBUILDVERSION
# Call eclipse headless to process CDT releng build scripts
pushd org.eclipse.cdt.releng
%{java} -cp $SDK/startup.jar \
     -Duser.home=$homedir                        \
     -DbuildId=%{build_id} \
     -DbranchVersion=%{version} \
     -DforceContextQualifier=%{build_id} \
-XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
-XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
-XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
-XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
    -application org.eclipse.ant.core.antRunner \
    -DbuildId=%{build_id} \
    -DbranchVersion=%{version} \
    -DforceContextQualifier=%{build_id} \
    -DjavacFailOnError=true \
    -DdontUnzip=true \
    -DbaseLocation=$SDK \
    -Dpde.build.scripts=$PDEDIR/scripts \
    -DdontFetchAnything=true \
    -DskipFetch=true
popd


## Autotools has dependencies on CDT so we must add these to the SDK directory

unzip -o org.eclipse.cdt.releng/results/I.%{build_id}/cdt-master-%{version}-%{build_id}.zip -d $SDK

## Autotools build
pushd autotools
%{java} -cp $SDK/startup.jar \
          -Duser.home=$homedir                        \
-XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
-XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
-XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
-XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
     -application org.eclipse.ant.core.antRunner \
     -Duser.home=$homedir                        \
     -Dtype=feature                                    \
     -Did=com.redhat.eclipse.cdt.autotools.feature         \
     -DsourceDirectory=$(pwd)                          \
     -DbaseLocation=$SDK                               \
     -Dbuilder=$PDEDIR/templates/package-build  \
     -f $PDEDIR/scripts/build.xml

popd


## Cppunit build
#pushd cppunit
#java -cp $SDK/startup.jar \
#     -Duser.home=$homedir                        \
#     org.eclipse.core.launcher.Main             \
#     -application org.eclipse.ant.core.antRunner       \
#     -Dtype=feature                                    \
#     -Did=org.eclipse.cdt.cppunit                      \
#     -DsourceDirectory=$(pwd)                          \
#     -DbaseLocation=$SDK                               \
#     -Dbuilder=$PDEDIR/templates/package-build  \
#     -f $PDEDIR/scripts/build.xml
#popd

%install
rm -rf ${RPM_BUILD_ROOT}

# Eclipse may try to write to the home directory.
mkdir -p home
homedir=$(cd home > /dev/null && pwd)

installDir=${RPM_BUILD_ROOT}/%{eclipse_base}/dropins/cdt
mylynInstallDir=${installDir}-mylyn
sdkInstallDir=${installDir}-sdk
install -d -m755 $installDir
install -d -m755 $mylynInstallDir
install -d -m755 $sdkInstallDir

unzip -q -o org.eclipse.cdt.releng/results/I.%{build_id}/cdt-master-%{version}-%{build_id}.zip \
-d $installDir/eclipse

rm $installDir/eclipse/site.xml
rm $installDir/eclipse/pack.properties

# Unpack all existing feature jars
for x in $installDir/eclipse/features/*.jar; do
  dirname=`echo $x | sed -e 's:\\(.*\\)\\.jar:\\1:g'`
  mkdir -p $dirname
  unzip -q $x -d $dirname
  rm $x
done

# Autotools install
pushd autotools
unzip -qq -d $installDir build/rpmBuild/com.redhat.eclipse.cdt.autotools.feature.zip
popd

mkdir -p $mylynInstallDir/eclipse/features $mylynInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*mylyn* $mylynInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*mylyn* $mylynInstallDir/eclipse/plugins

mkdir -p $sdkInstallDir/eclipse/features $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*source* $sdkInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*source* $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/plugins/org.eclipse.cdt.doc.isv_* $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*sdk* $sdkInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*sdk* $sdkInstallDir/eclipse/plugins

rm -rf $installDir/eclipse/features/org.eclipse.cdt.master_*
rm -rf $installDir/eclipse/plugins/org.eclipse.ant.optional.junit_*
rm -rf $installDir/eclipse/plugins/org.eclipse.test_*

## Cppunit install
#pushd cppunit
#unzip -qq -d $RPM_BUILD_ROOT%{eclipse_base}/dropins/cdt build/rpmBuild/org.eclipse.cdt.cppunit.zip
#popd

# Generate p2 metadata for CDT
pushd $installDir/eclipse
eclipse \
-nosplash \
-application \
org.eclipse.equinox.p2.metadata.generator.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "Eclipse CDT" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT" \
-metadataRepositoryName "CDT" \
-vmargs \
-Duser.home=$homedir

mv repo/content.xml .
rm -rf repo
popd

# Generate p2 metadata for CDT Mylyn Bridge
pushd $mylynInstallDir/eclipse
eclipse \
-nosplash \
-application \
org.eclipse.equinox.p2.metadata.generator.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "CDT Mylyn Bridge" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT Mylyn" \
-metadataRepositoryName "CDT Mylyn" \
-vmargs \
-Duser.home=$homedir

mv repo/content.xml .
rm -rf repo
popd

# Generate p2 metadata for CDT SDK
pushd $sdkInstallDir/eclipse
eclipse \
-nosplash \
-application \
org.eclipse.equinox.p2.metadata.generator.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "Eclipse CDT SDK" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT SDK" \
-metadataRepositoryName "CDT SDK" \
-vmargs \
-Duser.home=$homedir

mv repo/content.xml .
rm -rf repo
popd

mkdir -p ${installDir}-tests/plugins
mkdir -p ${installDir}-tests/features
mv ${installDir}/eclipse/plugins/*test* \
  ${installDir}-tests/plugins
mv ${installDir}/eclipse/features/*test* \
  ${installDir}-tests/features
for x in ${installDir}-tests/plugins/*.jar; do
  dirname=`echo $x | sed -e 's:\\(.*\\)\\.jar:\\1:g'`
  mkdir -p $dirname
  unzip -q $x -d $dirname
  rm $x
done
cp -p %{SOURCE5} ${installDir}-tests/runtests
chmod 755 ${installDir}-tests/runtests
%if ! %{ship_tests}
%if ! %{run_tests}
rm -rf ${installDir}-tests
%endif
%endif

%{gcj_compile}

%if %{run_tests}
%check
installDir=${RPM_BUILD_ROOT}/%{eclipse_base}/dropins/cdt
# Copy the SDK to simulate real system
rm -rf SDK.fortests
cp -rpL %{eclipse_base} SDK.fortests
# Remove any CDT or CDT tests we may have currently installed
rm -rf SDK.fortests/dropins/cdt*
cp -rpL $installDir SDK.fortests/dropins
# FIXME:  will also need to rename this if autotools goes
# s/com.redhat/org.eclipse
# The autotools plugin offers lots of completions but these cause issues
# with some of the tests which expect only a few completions.  We should
# update the tests or something ...
rm -rf SDK.fortests/dropins/cdt/eclipse/plugins/com.redhat*
cp -rpL ${installDir}-tests SDK.fortests/dropins
# FIXME:  I'd like to simulate real life with something like this ...
#chown -R root:root SDK.fortests
SDK.fortests/dropins/cdt-tests/runtests -e $(pwd)/SDK.fortests
w3m -cols 120 -dump results-*/html/org.eclipse.cdt.testing.html
%if ! %{ship_tests}
rm -rf ${installDir}-tests
%endif
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
%{eclipse_base}/dropins/cdt
%if %{gcj_support}
%{_libdir}/gcj/%{name}
%endif

%files sdk
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-sdk

%files mylyn
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-mylyn

%if %{ship_tests}
%files tests
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-tests
%endif


