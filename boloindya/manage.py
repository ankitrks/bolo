#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")    
    os.environ["FFMPEG_BINARY"] = "/usr/local/bin/ffmpeg"
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
