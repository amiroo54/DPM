# DPM - Dynamic Pie Menu Manager

Dynamic Pie Manager is a Blender add-on to dynamically add pie menus to different shortcuts and share them with others.

## Features

- Create custom pie menus with full Python actions
- Dynamic highlighting
- Per-mode keymaps
- Import/export of configurations
- Easy sharing of pie menu setups

## Installation

### Option 1: Install from Custom Extension Repository (Recommended)

1. Open Blender (version 4.2.0 or later)
2. Go to **Edit** → **Preferences** → **Get Extensions**
3. Click the **⚙** (Settings) icon in the top-right corner
4. Click **Add Remote Repository**
5. Enter the following repository URL:
   ```
   https://amiroo54.github.io/DPM/index.json
   ```
6. Click **OK** to add the repository
7. Search for "Dynamic Pie Menu Manager" in the Extensions list
8. Click **Install** to install the add-on
9. The add-on will be automatically updated when new versions are released

### Option 2: Manual Installation

1. Download the latest release ZIP file from the [releases page](https://github.com/amiroo54/DPM/releases)
2. In Blender, go to **Edit** → **Preferences** → **Add-ons**
3. Click **Install...** and select the downloaded ZIP file
4. Enable the add-on by checking the box next to "Interface: Dynamic Pie Menu Manager"

## Usage

After installation, you can access the Dynamic Pie Menu Manager from:
**Preferences** → **Add-ons** → **Dynamic Pie Menu Manager**

## For Developers/Maintainers

### Automated Extension Repository

This repository uses GitHub Actions to automatically build and publish the add-on to a custom Blender extension repository.

**Setup (One-time):**
1. Go to repository **Settings** → **Pages**
2. Under "Build and deployment", select **Source**: Deploy from a branch
3. Select branch: **gh-pages** and folder: **/ (root)**
4. Click **Save**

**How it works:**
- When changes are pushed to the `main` branch, a GitHub Actions workflow automatically:
  1. Creates a ZIP archive of the add-on
  2. Computes its SHA256 checksum
  3. Generates an `index.json` file following Blender's extension repository schema
  4. Publishes everything to the `gh-pages` branch
  5. GitHub Pages serves the extension repository at `https://amiroo54.github.io/DPM/index.json`

**Manual trigger:**
You can also manually trigger the workflow from the **Actions** tab → **Build Blender Extension Repository** → **Run workflow**

**Version management:**
Currently, versions are derived from the commit SHA. To use semantic versioning or git tags, see the comments in `.github/workflows/build-extension-repo.yml`.

## License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

## Credits

- **Author**: Amiroof
- **Inspired by**: Polyfjord's original idea
- **Development assistance**: ChatGPT
