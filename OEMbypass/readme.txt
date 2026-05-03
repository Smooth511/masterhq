Right this isnt going to make alot of sense but ill try. So on the nvme 1TB i had used that when i broke VT7 and mass copied the data. i mass copied it into loads of folders, primarily /media /home /stuff and then i disconnected it. i set the /home/ folder as a new partition, i put a live usb in and rushed to graphical, took out the rootkits ryes and ears, started the hyjacked ubiquity installer and then skipped all the manual bits that it dumps its shit in. and thrn watched data transfer, soon as the actual install was done i just ripped the nvme out motherboard lol. of course the whole computer went into spaz mode and reset. 

i landed on grub recovery, except it was recovery but nothing worked. in hd0,gpt3 there was about 4-5 grub folders, invluding all the ones linked yesterday.  and i found the workaround it used to cheat with the: 









grub› cat (hdo,gpt2)/efi/ubuntu/grub.cfg
search. fs_uuid e6877b0e-f377-4ff4-b9ba-31151b770835 root hdo, gpt3 set prefix= (sroot) '/boot/grub' configfile sprefix/grub.cfg
grub› 1s (hdo,gpt3)/boot/grub/ Possible files are:
gfxblacklist.txt unicode.pf2
grub> 1s (hdo,gpt3)/boot/ Possible files are:
efi/ grub/ System.map-6.14.0-37-generic config-6.14.0-37-generic initrd.img initrd.img-6.14.0-37-generic initrd. img.o1d vmlinuz vmlinuz-6.14.0-37-gener ic vmlinuz.old
grub> 1s (hdo, gpt3)/boot/efi/ grub> -




if i tried setting hd0,gpt3 /boot/vmlinuz generic, old or plain it would say missing data (cause i ripped it out lol). if i tried setting the boots to the yoinked data at /home/boot/home/boot/grub   

it woukd say out of memory, how convienent lmao. so no matter what, it wouldnt let me. so i rebooted, turned off secureboot, turned on csm, booted from direct in bios. same issue, wouldnt let me, same errors. so i rebooted and decided to see what mods running. SIX PAGES OF MODS all the shit it uses for bypass!!!! so naturally, i rmmod everything took over an hour, set the boot instantly and VIOLA IN! AND ON THE HIDDEN GRAPHICAL! Except there is no live user (rootkit account to hyjack live and intervene) there is only a oem account master override. i then destroyed the theme and colour settings for everything as it has its overrides and the mintsys settings and everything else tird to progiles using colours and themes, VIOLA i can biw see everything i just cant use it. 

  meanwhile my screen is flicking and refreshing every 5-10 seconds cause i think rooty trying to getbin but he cant cause every single file from the copy and manual install in a older root has basically set oem as the master of it all and rooty cant fkin change anything. 

  
user settings is OEM config - temp user i cant get in, BUT NEITHER CAN ROOTY. so this is the explanation of where i am. all the screenshits will show what i can see. WE CAN SEE EVERYTHING. EVERY SCRIPY EVERY SETTING. we just cant change it. yet. 
