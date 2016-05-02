# Project Setup

Create a local catkin workspace (e.g. in you home directory)
```sh
mkdir -p catkin_ws/src
cd catkin_ws
catkin_init_workspace ./src
```
One option is to clone the reobopatrol github repo into the src folder of your catkin_ws folder
```sh
git clone git@github.com:DeeVeX/Robo-Patrol.git src/robopatrol
```
Another option is to clone the github repos outside of the catkin_ws and create a symbolic link
```sh
git clone git@github.com:DeeVeX/Robo-Patrol.git
ln -s path_to_your_github_repos path_to_catkin_ws/src/robopatrol
```

# Build packages & Run robopatrol

To build all packages in the catkin workspace, change into your catkin_ws folder and run

```sh
catkin_make
```
Source your setup shell file

```sh
source devel/setup.bash
```

Now, you can run robopatrol

```sh
rosrun robopatrol robopatrol
```
This executes the script file ```scripts/robopatrol```

# Running the tests

To run the tests for all packages and show test results, change into your catkin_ws folder and run

```sh
catkin_make run_tests
catkin_test_results
```

Run nosetest manually
```sh
nosetests --where src/robopatrol/
```
