import subprocess


class Tunnel(object):
    def __init__(self, host_appname, svc_hostname, internal_port, external_port):
        self.host_appname = host_appname
        self.external_port = str(external_port)
        self.internal_port = str(internal_port)
        self.svc_hostname = svc_hostname
        self._cmd = [
            'cf',
            'ssh',
            '-T',
            '-L',
            '{}:{}:{}'.format(self.internal_port, svc_hostname, self.external_port),
            host_appname
        ]
        self._connection = None

    def run_command(self, cmd):
        try:
            output = subprocess.check_output(
                [
                    "cf",
                    "ssh",
                    "-c",
                    cmd,
                    "-L"
                    "{}:{}:{}".format(self.internal_port, self.svc_hostname, self.external_port),
                    self.host_appname
                ]
            )

        except subprocess.CalledProcessError as e:
            raise Exception("There was a problem initiating the SSH tunnel: " + e.message)

        else:
            return output

    def connect(self):
        if self._connection:
            pass

        else:
            try:
                self._connection = subprocess.Popen(self._cmd)

            except Exception as e:
                raise e

    def disconnect(self):
        if not self._connection:
            pass

        else:
            try:
                self._connection.kill()

            except Exception as e:
                raise e

            else:
                self._connection = None
