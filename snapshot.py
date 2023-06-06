#!/bin/python3

from datetime import datetime  # Allows us to have the timestamp
from subprocess import run  # Allows us to use the btrfs command
from configparser import RawConfigParser  # Allows us to read in a configuration file
from glob import glob  # Sorts the contents of the snapshot directory
from os import listdir, path, makedirs  # //
from sys import exit  # Exit the program if something is wrong
from argparse import ArgumentParser  # Pass arguments to the script

# -----------------------------------------------------------------------------------------
# Argument parser setup
argument_parser = ArgumentParser()
argument_parser.add_argument('-g', '--generate', action="store_true", help='generate configuration file')
argument_parser.add_argument('-c', '--create', action="store_true", help='create snapshots')
argument_parser.add_argument('-l', '--list', action="store_true", help='list snapshots')
argument_parser.add_argument('-d', '--delete', action="store_true", help='delete old snapshots')
argument_parser.add_argument('-w', '--wipe', action="store_true", help='wipe snapshots')
argument_parser.add_argument('-i', '--info', default='default', help='add additionnal information', required=False)
option = argument_parser.parse_args()

config_parser = RawConfigParser()
config_dir = '/etc/snapshot/snapshot.conf'


# -----------------------------------------------------------------------------------------
class Write:
    # Generate configuration
    def generate_config(self):
        # Ask if we really want to (re)-generate the config
        ask_generation = input("Do you want to generate the default configuration ? It will overwrite the old one (y|n): ")
        if ask_generation.lower() != "y":
            exit("Cancellation of the generation !")

        # Content of the config file
        config_parser.add_section('subvolumes')
        config_parser.set('subvolumes', 'root', '/')
        config_parser.set('subvolumes', 'home', '/home')

        config_parser.add_section('main')
        config_parser.set('main', 'snapshot_dir', '/.snapshots')
        config_parser.set('main', 'keep_snapshots', '3')

        try:
            # Create the directory if not exist
            makedirs(path.dirname(config_dir), exist_ok=True)

            # Write the config file
            with open(config_dir, 'w') as f:
                config_parser.write(f)

            with open(config_dir, "a") as f:
                f.write("# vim: ft=config")

            # Confirm the operation
            print("New configuration file created!")
        except:
            exit(f"Can't write {config_dir}.")


if option.generate:
    Write().generate_config()


# -----------------------------------------------------------------------------------------
class Read:
    # Variables
    def __init__(self):
        try:
            # Read the config file
            config_parser.read(config_dir)

            # Dictionary from each sections
            self.subvolume_dictionary = dict(config_parser.items('subvolumes'))
            main_dictionary = dict(config_parser.items('main'))

            # Constants from the main section
            self.snapshot_dir = str(main_dictionary['snapshot_dir'])
            self.keep_snapshots = int(main_dictionary['keep_snapshots'])
            self.current_date = datetime.now().strftime('%s')
        except:
            exit(f"Can't read {config_dir}, please (re)-generate it.")

    # Create snapshots
    def create_snapshot(self):
        for subvol_name in self.subvolume_dictionary:

            # Values from each items of the subvolumes section
            subvol_directory = str(self.subvolume_dictionary[subvol_name])
            subvol_information = option.info

            try:
                run(['btrfs', 'subvolume', 'snapshot', '-r', f'{subvol_directory}',
                    f'{self.snapshot_dir}/{self.current_date}_{subvol_information}_{subvol_name}'], check=True)
            except:
                exit("Creation of snapshots failed.")

    # Delete old snapshots
    def delete_snapshot(self):
        for subvol_name in self.subvolume_dictionary:

            # Sort every snapshots from the directory by date of creation
            old_snapshots = sorted(glob(path.join(self.snapshot_dir, f'*{subvol_name}')), key=path.getmtime)

            try:
                # Here I slice everything except the last snapshots
                for snap in old_snapshots[:-self.keep_snapshots]:
                    run(['btrfs', 'subvolume', 'delete', f'{snap}'], check=True)
            except:
                exit("Deletion of snapshots failed.")

    # List snapshots
    def list_snapshot(self):
        # Get every subvolumes from the snapshot dir
        snapshot_dictionary = listdir(f'{self.snapshot_dir}')
        i = -1

        for snapshot_name in snapshot_dictionary:
            snapshots_timestamp = snapshot_name.split('_')[0]
            snapshots_dates = datetime.fromtimestamp(int(snapshots_timestamp))

            i = i + 1
            date = snapshots_dates.strftime("%d %B")
            hour = snapshots_dates.strftime("%H:%M")

            print(f'[{i}] ', date, ' ', hour, ' ', self.snapshot_dir, ' ', snapshot_name)

    # Wipe all snapshots
    def wipe_snapshot(self):
        # Ask if we really want to delete all our subvolumes
        ask_wipe = input("Do you want to delete ALL your subvolumes ? This action is irreversible (y|n): ")
        if ask_wipe.lower() != "y":
            exit("Cancellation of the deletion !")

        # Get every subvolumes from the snapshot dir
        snapshot_dictionary = listdir(f'{self.snapshot_dir}')

        # Here I delete every subvolumes inside the snapshot dir
        for snapshot_name in snapshot_dictionary:
            try:
                run(['btrfs', 'subvolume', 'delete', f'{self.snapshot_dir}/{snapshot_name}'], check=True)
            except:
                exit("Deletion of snapshots failed.")


if option.create:
    Read().create_snapshot()
if option.list:
    Read().list_snapshot()
if option.delete:
    Read().delete_snapshot()
if option.wipe:
    Read().wipe_snapshot()
