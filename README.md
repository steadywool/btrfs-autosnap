# BTRFS automatic snapshot 🧶

Create snapshots automatically with a configuration file !

## Installation
To install this script, first clone this repository:
```
$ git clone https://github.com/kaniville/btrfs-autosnap
$ cd btrfs-autosnap
```

You can now copy the different files to their respective locations:
```
# mv snapshot.py /usr/local/bin/snapshot
```

```
# mkdir /etc/snapshot
# mv snapshot.conf /etc/snapshot/snapshot.conf
```

```
# mkdir /etc/pacman.d/hooks
# mv snapshot.hook /etc/pacman.d/hooks/snapshot.hook
```

## Usage
You can display the help by entering the command `snapshot --help`.

Snapshots are created automatically before each Archlinux update.

You can configure some options and choose which subvolumes will be snapshot by editing `/etc/snapshot/snapshot.conf`:
```conf
[subvolumes] # You can add subvolumes here
root = '/'

[main] # Constants
snapshot_dir = '/.snapshots'
keep_snapshots = 5
date_format = '%s'
```
