import subprocess, sys, os
import json
import rospy
import rospkg
import rosnode
import rosgraph
import requests

from std_srvs.srv import Empty

from robopatrol import srv

ROSPKG = rospkg.RosPack()

class MapService:

    processes = {}

    def __init__(self):
        args = rospy.myargv(argv=sys.argv)

        rospy.init_node('map_service')

        rospy.loginfo("map_service: init")

        self.rest_url = 'http://localhost:9998/maps'

        self.start_service = rospy.Service(
            'robopatrol/map_service/start',
            srv.MapServiceStart,
            self.handle_start_map_server_request
        )
        self.stop_service = rospy.Service(
            'robopatrol/map_service/stop',
            srv.MapServiceStop,
            self.handle_stop_map_server_request
        )
        self.record_service = rospy.Service(
            'robopatrol/map_service/record',
            srv.MapServiceRecord,
            self.handle_start_slam_gmapping_request
        )
        self.save_service = rospy.Service(
            'robopatrol/map_service/save',
            srv.MapServiceSave,
            self.handle_save_map_request
        )
        self.delete_service = rospy.Service(
            'robopatrol/map_service/delete',
            srv.MapServiceDelete,
            self.handle_delete_map_request
        )
        self.load_default_service = rospy.Service(
            'robopatrol/map_service/load_default',
            srv.MapServiceLoadDefault,
            self.handle_default_map_loading
        )

        try:
            self.load_default_maps()
        except requests.exceptions.RequestException, e:
            rospy.logwarn(e)

        if len(args) > 1:
            self.start_map_server(args[1])

        rospy.on_shutdown(self.shutdown)
        rospy.spin()

    def handle_save_map_request(self, request):
        data = {'name': request.name, 'filename': request.filename}
        success = False
        try:
            response = self.post_map(data)
            success = response.ok
        except requests.exceptions.RequestException, e:
            rospy.logwarn(e)

        return srv.MapServiceSaveResponse(success=success)

    def handle_delete_map_request(self, request):
        data = {'id': request.id}
        success = False
        try:
            response = self.delete_map(data)
            success = response.ok
        except requests.exceptions.RequestException, e:
            rospy.logwarn(e)

        return srv.MapServiceDeleteResponse(success=success)

    def handle_start_map_server_request(self, request):
        success = self.start_map_server(request.filename)

        return srv.MapServiceStartResponse(success=success)

    def handle_stop_map_server_request(self, request):
        success = self.stop_map_server()

        return srv.MapServiceStopResponse(success=success)

    def handle_start_slam_gmapping_request(self, request):
        success = self.start_slam_gmapping()

        return srv.MapServiceRecordResponse(success=success)

    def handle_default_map_loading(self, request):
        success = False
        try:
            success = self.load_default_maps()
        except requests.exceptions.RequestException, e:
            rospy.logwarn(e)

        return srv.MapServiceLoadDefaultResponse(success=success)

    def load_default_maps(self):
        default_maps = [{
            'name': 'Playground', 'filename': 'playground.yaml'
        }, {
            'name': 'Willow', 'filename': 'willow.yaml'
        }, {
            'name': 'ICC Lab', 'filename': 'icclab.yaml'
        }]
        maps = self.get_maps()

        for default_map in default_maps:
            exists = False
            for existing_map in maps:
                if existing_map['filename'] == default_map['filename']:
                    exists = True
                    break
            if not exists:
                response = self.post_map(default_map)

        return True

    def get_maps(self):
        response = requests.get(self.rest_url)
        data = json.loads(response.content)
        return data

    def get_map(self, map_id):
        url = '{0}/{1}'.format(self.rest_url, map_id)
        response = requests.get(url)
        data = response.json()
        return data

    def post_map(self, data):
        filename = data['filename']
        if filename.endswith('.yaml'):
            filename = filename[0:-5]

        filepath = '{0}/maps/{1}'.format(ROSPKG.get_path('robopatrol'), filename)

        headers = {'Content-type': 'application/json'}
        json_data = json.dumps(data)
        response = requests.post(self.rest_url, data=json_data, headers=headers)
        if response.ok:
            subprocess.call(['rosrun', 'map_server', 'map_saver', '-f', filepath])

        return response

    def delete_map(self, data):
        item = self.get_map(data['id'])
        headers = {'Content-type': 'application/json'}
        json_data = json.dumps(data)
        url = '{0}/{1}'.format(self.rest_url, data['id'])
        response = requests.delete(url, headers=headers)

        if response.ok:
            filename = item['filename']
            if filename.endswith('.yaml'):
                filename = filename[0:-5]
            filepath = '{0}/maps/{1}'.format(ROSPKG.get_path('robopatrol'), filename)

            os.remove('{0}.yaml'.format(filepath))
            os.remove('{0}.pgm'.format(filepath))

        return response

    def start_map_server(self, filename):
        self.stop_map_server()
        self.stop_slam_gmapping()

        map_file = '{0}/maps/{1}'.format(ROSPKG.get_path('robopatrol'), filename)

        rospy.loginfo("map_service: start map server")
        self.processes['map_server'] = subprocess.Popen(['rosrun', 'map_server', 'map_server', map_file])

        try:
            rospy.wait_for_service('/static_map', timeout=5)
            success = True
        except rospy.ROSException, e:
            success = False

        return success

    def stop_map_server(self):
        process = self.processes.pop('map_server', None)
        if process is not None:
            rospy.loginfo("map_service: stop map server")
            rospy.wait_for_service('/move_base/clear_costmaps')
            try:
                clear_costmaps = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)
                resp = clear_costmaps()
            except rospy.ServiceException, e:
                rospy.logwarn("map_service: clear costmaps failed")
            process.kill()
            self.cleanup('/map_server')

        return True

    def start_slam_gmapping(self):
        self.stop_slam_gmapping()
        self.stop_map_server()

        self.processes['gmapping'] = subprocess.Popen(['rosrun', 'gmapping', 'slam_gmapping'])

        try:
            rospy.wait_for_service('/dynamic_map', timeout=5)
            # for unknown reasons dynamic_map service is not callable
            # therefore waiting one second until everything is initialized
            rospy.sleep(1)
            success = True
        except rospy.ROSException, e:
            success = False

        rospy.loginfo("map_service: start gmapping")

        return success

    def stop_slam_gmapping(self):
        process = self.processes.pop('gmapping', None)
        if process is not None:
            rospy.loginfo("map_service: stop gmapping")
            process.kill()
            self.cleanup('/gmapping')

        return True

    def cleanup(self, node_name):
        master = rosgraph.Master(rosnode.ID)
        nodes_to_cleanup = [n for n in rosnode.get_node_names() if n.startswith(node_name)]
        rosnode.cleanup_master_blacklist(master, nodes_to_cleanup)

    def shutdown(self):
        rospy.loginfo("Shutdown robopatrol map service")
        self.stop_map_server()
        self.stop_slam_gmapping()
        self.start_service.shutdown()
        self.stop_service.shutdown()
        self.save_service.shutdown()
        self.delete_service.shutdown()
        self.record_service.shutdown()
        self.load_default_service.shutdown()
