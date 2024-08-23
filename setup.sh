#!/bin/bash

set -e  
error_handler() {
    echo "Error occurred on line $1"
    exit 1
}


trap 'error_handler $LINENO' ERR

echo "Starting script..."

sudo apt update
sudo apt upgrade

sudo apt install -y build-essential libncurses-dev bison flex libssl-dev \
libelf-dev libmpc-dev libgmp-dev libmpfr-dev grub-pc-bin \
syslinux xorriso debootstrap bc kmod cpio dosfstools mtools busybox-static \
bzip2 tar gzip rsync u-boot-tools gawk texinfo build-essential \
gcc g++ make zlib1g-dev autoconf automake m4 patch perl python3 multipath-tools grub-pc grub-pc-bin grub-common \
mkisofs 


WORKDIR="/home/zyh/linuxbuild"
KERNEL_VERSION="6.5"
BUSYBOX_VERSION="1.34.1"
BINUTILS_VERSION="2.41"
GCC_VERSION="14.2.0"
GLIBC_VERSION="2.38"
ROOTFS="$WORKDIR/rootfs"
DISK="sda"
DISK_IMAGE="$WORKDIR/minimal_linux.img"
MOUNTDIR="$WORKDIR/mnt"
BOOT_IMG="$ROOTFS/boot/grub/boot.img"
export CFLAGS="-O2 -Wno-error"
export CXXFLAGS="-O2 -Wno-error"


sudo mkdir -p "$WORKDIR"
sudo chmod 777 $WORKDIR

cd "$WORKDIR"
sudo wget https://ftp.gnu.org/gnu/binutils/binutils-$BINUTILS_VERSION.tar.xz
sudo wget https://ftp.gnu.org/gnu/gcc/gcc-$GCC_VERSION/gcc-$GCC_VERSION.tar.xz
sudo wget https://ftp.gnu.org/gnu/glibc/glibc-$GLIBC_VERSION.tar.xz
sudo wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-$KERNEL_VERSION.tar.xz
sudo tar -xf binutils-$BINUTILS_VERSION.tar.xz
sudo tar -xf gcc-$GCC_VERSION.tar.xz

cd $WORKDIR/gcc-$GCC_VERSION
./contrib/download_prerequisites

cd "$WORKDIR"
sudo tar -xf glibc-$GLIBC_VERSION.tar.xz
sudo tar -xvf linux-$KERNEL_VERSION.tar.xz


# 下载 GCC 依赖
cd "$WORKDIR/gcc-$GCC_VERSION"
./contrib/download_prerequisites

# Binutils
cd "$WORKDIR/cross-toolchain"
sudo mkdir -p build-binutils
cd build-binutils
sudo $WORKDIR/binutils-$BINUTILS_VERSION/configure --target=x86_64-linux-gnu --prefix=$WORKDIR/cross-toolchain \
--disable-multilib
sudo make -j$(nproc)
sudo make install


export PATH="$WORKDIR/cross-toolchain/bin:$PATH"
export LD_LIBRARY_PATH="$WORKDIR/cross-toolchain/lib:$WORKDIR/cross-toolchain/lib64:$LD_LIBRARY_PATH"
export C_INCLUDE_PATH="$WORKDIR/cross-toolchain/include:$C_INCLUDE_PATH"
export CPLUS_INCLUDE_PATH="$WORKDIR/cross-toolchain/include:$CPLUS_INCLUDE_PATH"

# GCC
cd "$WORKDIR/cross-toolchain"
sudo mkdir -p build-gcc
cd build-gcc
sudo $WORKDIR/gcc-$GCC_VERSION/configure --target=x86_64-linux-gnu --prefix=$WORKDIR/cross-toolchain \
--enable-languages=c,c++ --disable-multilib --disable-decimal-float --with-newlib \
--disable-nls --disable-libmudflap --disable-libssp \
CFLAGS="-O2 -Wno-error=attributes" CXXFLAGS="-O2 -Wno-error=attributes"
sudo make all-gcc -j$(nproc)
sudo make install-gcc

#Kernel_headers
cd "$WORKDIR/linux-$KERNEL_VERSION"
sudo make x86_64_defconfig
sudo make ARCH=x86_64 target=headers_check
sudo make ARCH=x86_64 -j$(nproc) INSTALL_HDR_PATH=$WORKDIR/cross-toolchain/x86_64-linux-gnu headers_install

# GLIBC
cd "$WORKDIR/cross-toolchain"
sudo mkdir -p build-glibc
cd build-glibc
sudo $WORKDIR/glibc-$GLIBC_VERSION/configure --prefix=$WORKDIR/cross-toolchain/x86_64-linux-gnu --host=x86_64-linux-gnu \
--target=x86_64-linux-gnu --disable-multilib --disable-nls --enable-shared \
CFLAGS="-O2 -Wno-error=attributes -U_FORTIFY_SOURCE" CXXFLAGS="-O2 -Wno-error=attributes"
sudo make -j$(nproc)
sudo make install

#GCC
cd "$WORKDIR/cross-toolchain/build-gcc"
sudo make all-target-libgcc -j$(nproc)  # 构建 libgcc
sudo make install-target-libgcc  # 安装 libgcc
sudo make -j$(nproc)
sudo make install

# Kernel
CROSS_COMPILE=$WORKDIR/cross-toolchain/bin/x86_64-linux-gnu-

cd $WORKDIR/linux-$KERNEL_VERSION

./scripts/config --file .config --set-str SYSTEM_TRUSTED_KEYS ''

./scripts/config --file .config --set-str SYSTEM_REVOCATION_KEYS ''
sudo make ARCH=x86_64 CROSS_COMPILE=$CROSS_COMPILE x86_64_defconfig
sudo sed -i 's/^# CONFIG_BLK_DEV_INITRD=*/CONFIG_BLK_DEV_INITRD=y/' .config
sudo sed -i 's/^# CONFIG_BLK_DEV_RAM=*/CONFIG_BLK_DEV_RAM=y/' .config
sudo sed -i '/^CONFIG_BLK_DEV_RAM_SIZE=/d' .config
sudo sed -i '$a CONFIG_BLK_DEV_RAM_SIZE=65536' .config
grep CONFIG_BLK_DEV_INITRD .config
grep CONFIG_BLK_DEV_RAM .config
grep CONFIG_BLK_DEV_RAM_SIZE .config
sudo make -j$(nproc)


# busyBox
cd "$WORKDIR"
sudo wget https://busybox.net/downloads/busybox-$BUSYBOX_VERSION.tar.bz2
sudo tar -xvf busybox-$BUSYBOX_VERSION.tar.bz2

cd $WORKDIR/busybox-$BUSYBOX_VERSION
sudo chmod 777 $WORKDIR/busybox-$BUSYBOX_VERSION
sudo make ARCH=x86_64 CROSS_COMPILE=$CROSS_COMPILE defconfig
#静态编译
sudo sed -i '/^CONFIG_STATIC=/d' .config
sudo sed -i '$a CONFIG_STATIC=y' .config
sudo sed -i 's/CONFIG_TC=y/CONFIG_TC=n/' .config
sudo sed -i 's/# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config
grep CONFIG_STATIC .config
grep CONFIG_TC .config
sudo make -j$(nproc)
sudo make install


cd $WORKDIR/busybox-$BUSYBOX_VERSION/_install
sudo mkdir etc dev mnt
sudo mkdir -p proc sys tmp mnt
sudo mkdir -p etc/init.d/
sudo cat << EOF | sudo tee $WORKDIR/busybox-$BUSYBOX_VERSION/_install/etc/fstab
proc    /proc   proc    defaults    0   0
sysfs   /sys    sysfs   defaults    0   0
tmpfs   /tmp    tmpfs   defaults    0   0
EOF
sudo cat << EOF | sudo tee $WORKDIR/busybox-$BUSYBOX_VERSION/_install/etc/init.d/rcS
#!/bin/sh
PATH=/sbin:/bin:/usr/sbin:/usr/bin
runlevel=S
prevlevel=N
umask 022
export PATH runlevel prevlevel
/bin/mount -a  
echo /sbin/mdev>/proc/sys/kernel/hotplug
mdev -s                 
/bin/hostname -F /etc/sysconfig/HOSTNAME
EOF
sudo chmod 755 $WORKDIR/busybox-$BUSYBOX_VERSION/_install/etc/init.d/rcS
sudo cat << EOF | sudo tee $WORKDIR/busybox-$BUSYBOX_VERSION/_install/etc/inittab
::sysinit:/etc/init.d/rcS   
::askfirst:-/bin/sh         
::ctrlaltdel:/sbin/reboot   
::restart:/sbin/init
::showdown:/bin/mount      
EOF
sudo chmod 755 $WORKDIR/busybox-$BUSYBOX_VERSION/_install/etc/inittab
sudo cat << EOF | sudo tee $WORKDIR/busybox-$BUSYBOX_VERSION/_install/etc/profile
#/etc/profile:system-wide .profile file for the Bourne shells
#!/bin/sh
#vim:syntax=sh
#No core file by defaults
#ulimit -S -c 0>/dev/null 2>&1
USER="id -un"
LOGNAME=$USER
PS1='[root@sb]#'
PATH=$PATH
HOSTNAME='/bin/hostname'
export USER LOGNAME PS1 PATH
EOF


#制作iso
sudo mkdir -p  $WORKDIR/rootfs
sudo chmod 777 $WORKDIR/rootfs
sudo mkdir -p $WORKDIR/rootfs/lib64

cd $WORKDIR/rootfs
sudo cp -fr $WORKDIR/busybox-$BUSYBOX_VERSION/_install/* $WORKDIR/rootfs/
sudo mkdir -p dev etc lib64 mnt opt proc root sys tmp var home
sudo mkdir -p $WORKDIR/rootfs/lib64/ 
sudo cp $WORKDIR/cross-toolchain/lib64/* ./lib64/
sudo rm rootfs/lib64/*.a
sudo strip $WORKDIR/rootfs/lib64/*
sudo chmod 777 $WORKDIR/rootfs/etc/init.d/rcS
sudo chmod 777 $WORKDIR/rootfs/etc/inittab
sudo mknod ./dev/tty1 c 4 1
sudo mknod ./dev/tty2 c 4 2
sudo mknod ./dev/tty3 c 4 3
sudo mknod ./dev/tty4 c 4 4
sudo mknod ./dev/console c 5 1
sudo mknod ./dev/null c 1 3


cd $WORKDIR/rootfs
sudo ln -sv bin/busybox init
sudo find . | cpio -H newc -o | gzip -9 -n > ../initrd.gz

cd $WORKDIR
sudo wget https://mirrors.edge.kernel.org/pub/linux/utils/boot/syslinux/syslinux-4.04.tar.gz
sudo tar -xf syslinux-4.04.tar.gz



sudo mkdir -p $WORKDIR/iso

cd $WORKDIR/iso
sudo cp -rf $WORKDIR/initrd.gz $WORKDIR/iso
sudo cp $WORKDIR/linux-6.5/arch/x86/boot/bzImage $WORKDIR/iso
sudo cp $WORKDIR/syslinux-4.04/core/isolinux.bin $WORKDIR/iso


sudo cat << EOF | sudo tee $WORKDIR/iso/isolinux.cfg
display miniLinux
prompt 1
default 1
 
# Boot other devices
label a
    localboot 0x00
 
# PC-DOS
label 1
    kernel bzImage
    append initrd=initrd.gz
EOF

cd $WORKDIR
sudo mkisofs -o miniLinux.iso -b isolinux.bin -c boot.cat \
-no-emul-boot -boot-load-size 4 -boot-info-table ./iso



echo "Script completed successfully."

































