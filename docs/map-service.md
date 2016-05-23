# Map Service

A ROS-Service to start/stop the map-server and to create/delete maps.

The service adds on startup some default maps to the database (playground.yaml,
willow.yaml and icclab.yaml).

The service can also be used from the command line.

## Load default maps
```sh
rosservice call /robopatrol/map_service/load_default
```

## Start and stop map server

Start the map server:
```sh
rosservice call /robopatrol/map_service/start my-map.yaml
```
The map-file has to be in the maps folder.

Stop the map server:
```sh
rosservice call /robopatrol/map_service/stop
```

## Create map

To create a map, you have to start the slam-gmapping:
```sh
rosservice call /robopatrol/map_service/record
```

Save the recorded map:
```sh
rosservice call /robopatrol/map_service/save 'my-map.yaml' 'My Map'
```
The first argument is the filename, the second the map name. The file is
saved to the `/maps` folder.

Stop the slam-gmapping node:
```sh
rosservice call /robopatrol/map_service/stop
```

## Delete map
```sh
rosservice call /robopatrol/map_service/delete map-id
```
The map-id argument is the ID created from the database.
