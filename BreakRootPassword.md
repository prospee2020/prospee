# Reboot the system and press any key to stop the auto-boot from the default kernel. Press “e” after selecting the kernel line.
# When you are in edit mode, go to the line starting with linux16 and append rd.break to the end of this line.
# This will cause the machine to boot into emergency mode, which gives you root user privileges without you having to enter a root user password. Even if the root user password hasn’t been set, this still works.
# Press CTLR+x after appending the rd.break to the kernel. This will reboot the system into emergency mode.
Remount sysroot
First we will remount the sysroot file system in read write mode and then use chroot to got into a chroot jail:

# mount -o remount,rw /sysroot
# chroot /sysroot
Reset root password
Finally, type passwd command in the command line and set the new password for root user. You might get some warnings like “password fails dictionary check” if your password is weak. You may safely ignore the warning and set the password you want.

# passwd


SElinux relabeling
Make sure that all unlabeled files ( including shadow file ) gets relabeled during booting. Touching the hidden file autorelabel instructs SElinux to relabel the files changed outside of its regular context, like the file /etc/shadow.

# touch /.autorelabel

sync
To flush all cache to disk, type the command:

# sync
Reboot
Type twice the exit command to leave the chroot environment and log out. The system will apply some SELinux contexts and reboot. You can now log in using your newly set root password.
