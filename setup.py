## ! DO NOT MANUALLY INVOKE THIS setup.py, USE CATKIN INSTEAD

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    packages=['robopatrol'],
    package_dir={'': 'src'},
)

setup(
	name='Robopatrol',
	version='0.0.0',
	description='Robot doing patrols',
	install_requires=[
		'apscheduler',
		'json-schema'
	]
)

