# indigo-webcam

Provide actions for handling webcam images.

## NOTE

This plugin is still in early development stage.  There is very little error handling, so
please use at your own risk.  Feel free to open issues or refer to the plugin forum for
support or to file bugs.

## Requirements

[Indigo Pro](https://www.indigodomo.com) is required to get support for plugins.  If you
haven't tried Indigo and are interested in home automation, please give it a shot right
away...  You won't be disappointed!

## Installation

TODO

## Configuration

After installing the first time, you will be prompted for the plugin configuration.  You
can also access the plugin config at any time from the Plugins menu.

### Filename Formatting

Certain filenames support strftime() formatting strings.  This is a great way to add a timestamp
or other unique information to the name of the file.  For detailed usage on the available
options, consult the strftime.org documentation.  Some examples:

Include the YYYYMMDDHHMMSS timestamp: image-%Y%m%d%H%M%S.jpg

## Usage

The plugin creates a few new actions that can be executed as any Indigo action would.  This
means you could set them up based on a schedule, trigger or as part of an Action Group.

### Save File

Downloads an image from a URL and saves it to a local folder.

Eventually, I'd like some way to only keep images for a certain period of time.  For now,
all files are retained unless the template would override them.

### FTP Put

This action will copy an image from a given URL and upload to an FTP server.

