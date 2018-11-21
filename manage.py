#!/usr/bin/env python3.7

import os
import sys

print(os.getcwd())
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), "searchenginepy"))
    #sys.path.append(os.path.join(os.path.dirname(__file__), "searchengine"))
    #sys.path.append(os.path.join(os.path.dirname(__file__), "searchsite"))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchsite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
