"""
The flask application package.
"""

from flask import Flask
import cfg_module

app = Flask(__name__)

app.config.from_object(cfg_module.Cfg)

import steerapi
