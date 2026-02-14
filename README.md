# DPM - Dynamic Pie Menu Manager

Dynamic Pie Manager is a Blender add-on to dynamically add pie menus to different shortcuts and share them with others.

## Features

- Create custom pie menus with full Python actions
- Dynamic highlighting
- Per-mode keymaps
- Import/export of configurations
- Easy sharing of pie menu setups

## Installation

1. Download the latest release ZIP file from the [releases page](https://github.com/amiroo54/DPM/releases)
2. In Blender, go to **Edit** → **Preferences** → **Add-ons**
3. Click **Install...** and select the downloaded ZIP file
4. Enable the add-on by checking the box next to "Interface: Dynamic Pie Menu Manager"

## Usage

After installation, you can access the Dynamic Pie Menu Manager from:
**Preferences** → **Add-ons** → **Dynamic Pie Menu Manager**

There you can **Add new Pies**, **Edit existing pies** and **Import and Export Pies**.

### Adding Pies

By hitting **Add new Pie** button you can make a new blank pie menu. Here you can edit it's name, Enable and Disable it, Mark it for export and Remove it.

### Editing Pies

You can have up to 8 actions assigned to a pie menu. Each one has an icon, a direction (the direction it appears in the menu), a code and a highlight condition.

### Importing and Exporting pies

This is the main strength of this addon. You can mark the Pies you have designed for export, and get a json file which can be imported by anyone, or you can get a json file someone else made to use that. To see an example please refer to [my personal config](https://github.com/amiroo54/DPM/blob/main/configs/Personal.json).

## To Do

- [] Add a check to remove duplicate pies based on the uuid
- [] Add a global repository for people to share their configs
- [] Add support for more workspaces

## For Developers/Maintainers

### Automated Extension Repository

This repository uses GitHub Actions to automatically build and publish the add-on to github releases.

**Version management:**
Currently, versions are derived from the commit SHA. To use semantic versioning or git tags, see the comments in `.github/workflows/build-extension-repo.yml`.

## License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

## Credits

- **Author**: Amiroof
- **Inspired by**: Polyfjord's ["I made a free addon to work 4% faster in Blender!"](https://www.youtube.com/watch?v=JggpNfPA9iw) video.