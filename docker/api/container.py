import six
import warnings
from datetime import datetime

from .. import errors
from .. import utils
from ..utils.utils import create_networking_config, create_endpoint_config


class ContainerApiMixin(object):
    @utils.check_resource
    def attach(self, container, stdout=True, stderr=True,
               stream=False, logs=False):
        """
        Attach to a container.

        The ``.logs()`` function is a wrapper around this method, which you can
        use instead if you want to fetch/stream container output without first
        retrieving the entire backlog.

        Args:
            container (str): The container to attach to.
            stdout (bool): Include stdout.
            stderr (bool): Include stderr.
            stream (bool): Return container output progressively as an iterator
                of strings, rather than a single string.
            logs (bool): Include the container's previous output.

        Returns:
            By default, the container's output as a single string.

            If ``stream=True``, an iterator of output strings.
        """
        params = {
            'logs': logs and 1 or 0,
            'stdout': stdout and 1 or 0,
            'stderr': stderr and 1 or 0,
            'stream': stream and 1 or 0
        }

        headers = {
            'Connection': 'Upgrade',
            'Upgrade': 'tcp'
        }

        u = self._url("/containers/{0}/attach", container)
        response = self._post(u, headers=headers, params=params, stream=stream)

        return self._read_from_socket(response, stream)

    @utils.check_resource
    def attach_socket(self, container, params=None, ws=False):
        """
        Like ``attach``, but returns the underlying socket-like object for the
        HTTP request.

        Args:
            container (str): The container to attach to.
            params (dict): Dictionary of request parameters (e.g. ``stdout``,
                ``stderr``, ``stream``).
            ws (bool): Use websockets instead of raw HTTP.
        """
        if params is None:
            params = {
                'stdout': 1,
                'stderr': 1,
                'stream': 1
            }

        if ws:
            return self._attach_websocket(container, params)

        headers = {
            'Connection': 'Upgrade',
            'Upgrade': 'tcp'
        }

        u = self._url("/containers/{0}/attach", container)
        return self._get_raw_response_socket(
            self.post(
                u, None, params=self._attach_params(params), stream=True,
                headers=headers
            )
        )

    @utils.check_resource
    def commit(self, container, repository=None, tag=None, message=None,
               author=None, changes=None, conf=None):
        """
        Identical to the ``docker commit`` command.

        Args:
            container (str): The image hash of the container
            repository (str): The repository to push the image to
            tag (str): The tag to push
            message (str): A commit message
            author (str): The name of the author
            changes (str): Dockerfile instructions to apply while committing
            conf (dict): The configuration for the container. See the
                `Remote API documentation
                <https://docs.docker.com/reference/api/docker_remote_api/>`_
                for full details.
        """
        params = {
            'container': container,
            'repo': repository,
            'tag': tag,
            'comment': message,
            'author': author,
            'changes': changes
        }
        u = self._url("/commit")
        return self._result(self._post_json(u, data=conf, params=params),
                            json=True)

    def containers(self, quiet=False, all=False, trunc=False, latest=False,
                   since=None, before=None, limit=-1, size=False,
                   filters=None):
        """
        List containers. Identical to the ``docker ps`` command.

        Args:
            quiet (bool): Only display numeric Ids
            all (bool): Show all containers. Only running containers are shown
                by default trunc (bool): Truncate output
            latest (bool): Show only the latest created container, include
                non-running ones.
            since (str): Show only containers created since Id or Name, include
                non-running ones
            before (str): Show only container created before Id or Name,
                include non-running ones
            limit (int): Show `limit` last created containers, include
                non-running ones
            size (bool): Display sizes
            filters (dict): Filters to be processed on the image list.
                Available filters:

                - `exited` (int): Only containers with specified exit code
                - `status` (str): One of ``restarting``, ``running``,
                    ``paused``, ``exited``
                - `label` (str): format either ``"key"`` or ``"key=value"``
                - `id` (str): The id of the container.
                - `name` (str): The name of the container.
                - `ancestor` (str): Filter by container ancestor. Format of
                    ``<image-name>[:tag]``, ``<image-id>``, or
                    ``<image@digest>``.
                - `before` (str): Only containers created before a particular
                    container. Give the container name or id.
                - `since` (str): Only containers created after a particular
                    container. Give container name or id.

                A comprehensive list can be found in the documentation for
                `docker ps
                <https://docs.docker.com/engine/reference/commandline/ps>`_.

        Returns:
            A list of dicts, one per container
        """
        params = {
            'limit': 1 if latest else limit,
            'all': 1 if all else 0,
            'size': 1 if size else 0,
            'trunc_cmd': 1 if trunc else 0,
            'since': since,
            'before': before
        }
        if filters:
            params['filters'] = utils.convert_filters(filters)
        u = self._url("/containers/json")
        res = self._result(self._get(u, params=params), True)

        if quiet:
            return [{'Id': x['Id']} for x in res]
        if trunc:
            for x in res:
                x['Id'] = x['Id'][:12]
        return res

    @utils.check_resource
    def copy(self, container, resource):
        """
        Identical to the ``docker cp`` command. Get files/folders from the
        container.

        **Deprecated for API version >= 1.20.** Use
        :py:meth:`~ContainerApiMixin.get_archive` instead.

        Args:
            container (str): The container to copy from
            resource (str): The path within the container

        Returns:
            The contents of the file as a string
        """
        if utils.version_gte(self._version, '1.20'):
            warnings.warn(
                'Client.copy() is deprecated for API version >= 1.20, '
                'please use get_archive() instead',
                DeprecationWarning
            )
        res = self._post_json(
            self._url("/containers/{0}/copy".format(container)),
            data={"Resource": resource},
            stream=True
        )
        self._raise_for_status(res)
        return res.raw

    def create_container(self, image, command=None, hostname=None, user=None,
                         detach=False, stdin_open=False, tty=False,
                         mem_limit=None, ports=None, environment=None,
                         dns=None, volumes=None, volumes_from=None,
                         network_disabled=False, name=None, entrypoint=None,
                         cpu_shares=None, working_dir=None, domainname=None,
                         memswap_limit=None, cpuset=None, host_config=None,
                         mac_address=None, labels=None, volume_driver=None,
                         stop_signal=None, networking_config=None):
        """
        Creates a container. Parameters are similar to those for the ``docker
        run`` command except it doesn't support the attach options (``-a``).

        The arguments that are passed directly to this function are
        host-independent configuration options. Host-specific configuration
        is passed with the `host_config` argument. You'll normally want to
        use this method in combination with the :py:meth:`create_host_config`
        method to generate ``host_config``.

        **Port bindings**

        Port binding is done in two parts: first, provide a list of ports to
        open inside the container with the ``ports`` parameter, then declare
        bindings with the ``host_config`` parameter. For example:

        .. code-block:: python

            container_id = cli.create_container(
                'busybox', 'ls', ports=[1111, 2222],
                host_config=cli.create_host_config(port_bindings={
                    1111: 4567,
                    2222: None
                })
            )


        You can limit the host address on which the port will be exposed like
        such:

        .. code-block:: python

            cli.create_host_config(port_bindings={1111: ('127.0.0.1', 4567)})

        Or without host port assignment:

        .. code-block:: python

            cli.create_host_config(port_bindings={1111: ('127.0.0.1',)})

        If you wish to use UDP instead of TCP (default), you need to declare
        ports as such in both the config and host config:

        .. code-block:: python

            container_id = cli.create_container(
                'busybox', 'ls', ports=[(1111, 'udp'), 2222],
                host_config=cli.create_host_config(port_bindings={
                    '1111/udp': 4567, 2222: None
                })
            )

        To bind multiple host ports to a single container port, use the
        following syntax:

        .. code-block:: python

            cli.create_host_config(port_bindings={
                1111: [1234, 4567]
            })

        You can also bind multiple IPs to a single container port:

        .. code-block:: python

            cli.create_host_config(port_bindings={
                1111: [
                    ('192.168.0.100', 1234),
                    ('192.168.0.101', 1234)
                ]
            })

        **Using volumes**

        Volume declaration is done in two parts. Provide a list of mountpoints
        to the with the ``volumes`` parameter, and declare mappings in the
        ``host_config`` section.

        .. code-block:: python

            container_id = cli.create_container(
                'busybox', 'ls', volumes=['/mnt/vol1', '/mnt/vol2'],
                host_config=cli.create_host_config(binds={
                    '/home/user1/': {
                        'bind': '/mnt/vol2',
                        'mode': 'rw',
                    },
                    '/var/www': {
                        'bind': '/mnt/vol1',
                        'mode': 'ro',
                    }
                })
            )

        You can alternatively specify binds as a list. This code is equivalent
        to the example above:

        .. code-block:: python

            container_id = cli.create_container(
                'busybox', 'ls', volumes=['/mnt/vol1', '/mnt/vol2'],
                host_config=cli.create_host_config(binds=[
                    '/home/user1/:/mnt/vol2',
                    '/var/www:/mnt/vol1:ro',
                ])
            )

        Args:
            image (str): The image to run
            command (str or list): The command to be run in the container
            hostname (str): Optional hostname for the container
            user (str or int): Username or UID
            detach (bool): Detached mode: run container in the background and
                return container ID
            stdin_open (bool): Keep STDIN open even if not attached
            tty (bool): Allocate a pseudo-TTY
            mem_limit (float or str): Memory limit. Accepts float values (which
                represent the memory limit of the created container in bytes)
                or a string with a units identification char (``100000b``,
                ``1000k``, ``128m``, ``1g``). If a string is specified without
                a units character, bytes are assumed as an intended unit.
            ports (list of ints): A list of port numbers
            environment (dict or list): A dictionary or a list of strings in
                the following format ``["PASSWORD=xxx"]`` or
                ``{"PASSWORD": "xxx"}``.
            dns (list): DNS name servers. Deprecated since API version 1.10.
                Use ``host_config`` instead.
            dns_opt (list): Additional options to be added to the container's
                ``resolv.conf`` file
            volumes (str or list):
            volumes_from (list): List of container names or Ids to get
                volumes from.
            network_disabled (bool): Disable networking
            name (str): A name for the container
            entrypoint (str or list): An entrypoint
            working_dir (str): Path to the working directory
            domainname (str or list): Set custom DNS search domains
            memswap_limit (int):
            host_config (dict): A dictionary created with
                :py:meth:`create_host_config`.
            mac_address (str): The Mac Address to assign the container
            labels (dict or list): A dictionary of name-value labels (e.g.
                ``{"label1": "value1", "label2": "value2"}``) or a list of
                names of labels to set with empty values (e.g.
                ``["label1", "label2"]``)
            volume_driver (str): The name of a volume driver/plugin.
            stop_signal (str): The stop signal to use to stop the container
                (e.g. ``SIGINT``).
            networking_config (dict): A [NetworkingConfig](networks.md)
                dictionary

        Returns:
            A dictionary with an image 'Id' key and a 'Warnings' key.
        """
        if isinstance(volumes, six.string_types):
            volumes = [volumes, ]

        if host_config and utils.compare_version('1.15', self._version) < 0:
            raise errors.InvalidVersion(
                'host_config is not supported in API < 1.15'
            )

        config = self.create_container_config(
            image, command, hostname, user, detach, stdin_open,
            tty, mem_limit, ports, environment, dns, volumes, volumes_from,
            network_disabled, entrypoint, cpu_shares, working_dir, domainname,
            memswap_limit, cpuset, host_config, mac_address, labels,
            volume_driver, stop_signal, networking_config,
        )
        return self.create_container_from_config(config, name)

    def create_container_config(self, *args, **kwargs):
        return utils.create_container_config(self._version, *args, **kwargs)

    def create_container_from_config(self, config, name=None):
        u = self._url("/containers/create")
        params = {
            'name': name
        }
        res = self._post_json(u, data=config, params=params)
        return self._result(res, True)

    def create_host_config(self, *args, **kwargs):
        """
        Create a dictionary for the ``host_config`` argument to
        :py:meth:`create_container`.

        Args:
            binds (dict): Volumes to bind. See :py:meth:`create_container`
                    for more information.
            blkio_weight_device: Block IO weight (relative device weight) in
                the form of: ``[{"Path": "device_path", "Weight": weight}]``.
            blkio_weight: Block IO weight (relative weight), accepts a weight
                value between 10 and 1000.
            cap_add (list of str): Add kernel capabilities. For example,
                ``["SYS_ADMIN", "MKNOD"]``.
            cap_drop (list of str): Drop kernel capabilities.
            cpu_group (int): The length of a CPU period in microseconds.
            cpu_period (int): Microseconds of CPU time that the container can
                get in a CPU period.
            cpu_shares (int): CPU shares (relative weight).
            cpuset_cpus (str): CPUs in which to allow execution (``0-3``,
                ``0,1``).
            device_read_bps: Limit read rate (bytes per second) from a device
                in the form of: `[{"Path": "device_path", "Rate": rate}]`
            device_read_iops: Limit read rate (IO per second) from a device.
            device_write_bps: Limit write rate (bytes per second) from a
                device.
            device_write_iops: Limit write rate (IO per second) from a device.
            devices (list): Expose host devices to the container, as a list
                of strings in the form
                ``<path_on_host>:<path_in_container>:<cgroup_permissions>``.

                For example, ``/dev/sda:/dev/xvda:rwm`` allows the container
                to have read-write access to the host's ``/dev/sda`` via a
                node named ``/dev/xvda`` inside the container.
            dns (list): Set custom DNS servers.
            dns_search (list): DNS search domains.
            extra_hosts (dict): Addtional hostnames to resolve inside the
                container, as a mapping of hostname to IP address.
            group_add (list): List of additional group names and/or IDs that
                the container process will run as.
            ipc_mode (str): Set the IPC mode for the container.
            links (dict or list of tuples): Either a dictionary mapping name
                to alias or as a list of ``(name, alias)`` tuples.
            log_config (dict): Logging configuration, as a dictionary with
                keys:

                - ``type`` The logging driver name.
                - ``config`` A dictionary of configuration for the logging
                  driver.

            lxc_conf (dict): LXC config.
            mem_limit (float or str): Memory limit. Accepts float values
                (which represent the memory limit of the created container in
                bytes) or a string with a units identification char
                (``100000b``, ``1000k``, ``128m``, ``1g``). If a string is
                specified without a units character, bytes are assumed as an
            mem_swappiness (int): Tune a container's memory swappiness
                behavior. Accepts number between 0 and 100.
            memswap_limit (str or int): Maximum amount of memory + swap a
                container is allowed to consume.
            network_mode (str): One of:

                - ``bridge`` Create a new network stack for the container on
                  on the bridge network.
                - ``none`` No networking for this container.
                - ``container:<name|id>`` Reuse another container's network
                  stack.
                - ``host`` Use the host network stack.
            oom_kill_disable (bool): Whether to disable OOM killer.
            oom_score_adj (int): An integer value containing the score given
                to the container in order to tune OOM killer preferences.
            pid_mode (str): If set to ``host``, use the host PID namespace
                inside the container.
            pids_limit (int): Tune a container's pids limit. Set ``-1`` for
                unlimited.
            port_bindings (dict): See :py:meth:`create_container`
                    for more information.
            privileged (bool): Give extended privileges to this container.
            publish_all_ports (bool): Publish all ports to the host.
            read_only (bool): Mount the container's root filesystem as read
                only.
            restart_policy (dict): Restart the container when it exits.
                Configured as a dictionary with keys:

                - ``Name`` One of ``on-failure``, or ``always``.
                - ``MaximumRetryCount`` Number of times to restart the
                  container on failure.
            security_opt (list): A list of string values to customize labels
                for MLS systems, such as SELinux.
            shm_size (str or int): Size of /dev/shm (e.g. ``1G``).
            sysctls (dict): Kernel parameters to set in the container.
            tmpfs (dict): Temporary filesystems to mount, as a dictionary
                mapping a path inside the container to options for that path.

                For example:

                .. code-block:: python

                    {
                        '/mnt/vol2': '',
                        '/mnt/vol1': 'size=3G,uid=1000'
                    }

            ulimits (list): Ulimits to set inside the container, as a list of
                dicts.
            userns_mode (str): Sets the user namespace mode for the container
                when user namespace remapping option is enabled. Supported
                values are: ``host``
            volumes_from (list): List of container names or IDs to get
                volumes from.


        Returns:
            (dict) A dictionary which can be passed to the ``host_config``
            argument to :py:meth:`create_container`.

        Example:

            >>> cli.create_host_config(privileged=True, cap_drop=['MKNOD'],
                                       volumes_from=['nostalgic_newton'])
            {'CapDrop': ['MKNOD'], 'LxcConf': None, 'Privileged': True,
             'VolumesFrom': ['nostalgic_newton'], 'PublishAllPorts': False}

"""
        if not kwargs:
            kwargs = {}
        if 'version' in kwargs:
            raise TypeError(
                "create_host_config() got an unexpected "
                "keyword argument 'version'"
            )
        kwargs['version'] = self._version
        return utils.create_host_config(*args, **kwargs)

    def create_networking_config(self, *args, **kwargs):
        return create_networking_config(*args, **kwargs)

    def create_endpoint_config(self, *args, **kwargs):
        return create_endpoint_config(self._version, *args, **kwargs)

    @utils.check_resource
    def diff(self, container):
        """
        Inspect changes on a container's filesystem.

        Args:
            container (str): The container to diff

        Returns:
            (str)
        """
        return self._result(
            self._get(self._url("/containers/{0}/changes", container)), True
        )

    @utils.check_resource
    def export(self, container):
        """
        Export the contents of a filesystem as a tar archive to STDOUT.

        Args:
            container (str): The container to export

        Returns:
            (str): The filesystem tar archive
        """
        res = self._get(
            self._url("/containers/{0}/export", container), stream=True
        )
        self._raise_for_status(res)
        return res.raw

    @utils.check_resource
    @utils.minimum_version('1.20')
    def get_archive(self, container, path):
        """
        Retrieve a file or folder from a container in the form of a tar
        archive.

        Args:
            container (str): The container where the file is located
            path (str): Path to the file or folder to retrieve

        Returns:
            (tuple): First element is a raw tar data stream. Second element is
            a dict containing ``stat`` information on the specified ``path``.
        """
        params = {
            'path': path
        }
        url = self._url('/containers/{0}/archive', container)
        res = self._get(url, params=params, stream=True)
        self._raise_for_status(res)
        encoded_stat = res.headers.get('x-docker-container-path-stat')
        return (
            res.raw,
            utils.decode_json_header(encoded_stat) if encoded_stat else None
        )

    @utils.check_resource
    def inspect_container(self, container):
        """
        Identical to the `docker inspect` command, but only for containers.

        Args:
            container (str): The container to inspect

        Returns:
            (dict): Similar to the output of `docker inspect`, but as a
            single dict
        """
        return self._result(
            self._get(self._url("/containers/{0}/json", container)), True
        )

    @utils.check_resource
    def kill(self, container, signal=None):
        """
        Kill a container or send a signal to a container.

        Args:
            container (str): The container to kill
            signal (str or int): The signal to send. Defaults to ``SIGKILL``
        """
        url = self._url("/containers/{0}/kill", container)
        params = {}
        if signal is not None:
            if not isinstance(signal, six.string_types):
                signal = int(signal)
            params['signal'] = signal
        res = self._post(url, params=params)

        self._raise_for_status(res)

    @utils.check_resource
    def logs(self, container, stdout=True, stderr=True, stream=False,
             timestamps=False, tail='all', since=None, follow=None):
        """
        Identical to the ``docker logs`` command. The ``stream`` parameter
        makes the ``logs`` function return a blocking generator you can iterate
        over to retrieve log output as it happens.

        Args:
            container (str): The container to get logs from
            stdout (bool): Get STDOUT
            stderr (bool): Get STDERR
            stream (bool): Stream the response
            timestamps (bool): Show timestamps
            tail (str or int): Output specified number of lines at the end of
                logs. Either an integer of number of lines or the string
                ``all``. Default ``all``
            since (datetime or int): Show logs since a given datetime or
                integer epoch (in seconds)
            follow (bool): Follow log output

        Returns:
            (generator or str)
        """
        if utils.compare_version('1.11', self._version) >= 0:
            if follow is None:
                follow = stream
            params = {'stderr': stderr and 1 or 0,
                      'stdout': stdout and 1 or 0,
                      'timestamps': timestamps and 1 or 0,
                      'follow': follow and 1 or 0,
                      }
            if utils.compare_version('1.13', self._version) >= 0:
                if tail != 'all' and (not isinstance(tail, int) or tail < 0):
                    tail = 'all'
                params['tail'] = tail

            if since is not None:
                if utils.compare_version('1.19', self._version) < 0:
                    raise errors.InvalidVersion(
                        'since is not supported in API < 1.19'
                    )
                else:
                    if isinstance(since, datetime):
                        params['since'] = utils.datetime_to_timestamp(since)
                    elif (isinstance(since, int) and since > 0):
                        params['since'] = since
            url = self._url("/containers/{0}/logs", container)
            res = self._get(url, params=params, stream=stream)
            return self._get_result(container, stream, res)
        return self.attach(
            container,
            stdout=stdout,
            stderr=stderr,
            stream=stream,
            logs=True
        )

    @utils.check_resource
    def pause(self, container):
        """
        Pauses all processes within a container.

        Args:
            container (str): The container to pause
        """
        url = self._url('/containers/{0}/pause', container)
        res = self._post(url)
        self._raise_for_status(res)

    @utils.check_resource
    def port(self, container, private_port):
        """
        Lookup the public-facing port that is NAT-ed to ``private_port``.
        Identical to the ``docker port`` command.

        Args:
            container (str): The container to look up
            private_port (int): The private port to inspect

        Returns:
            (list of dict): The mapping for the host ports

        Example:
            .. code-block:: bash

                $ docker run -d -p 80:80 ubuntu:14.04 /bin/sleep 30
                7174d6347063a83f412fad6124c99cffd25ffe1a0807eb4b7f9cec76ac8cb43b

            .. code-block:: python

                >>> cli.port('7174d6347063', 80)
                [{'HostIp': '0.0.0.0', 'HostPort': '80'}]
        """
        res = self._get(self._url("/containers/{0}/json", container))
        self._raise_for_status(res)
        json_ = res.json()
        private_port = str(private_port)
        h_ports = None

        # Port settings is None when the container is running with
        # network_mode=host.
        port_settings = json_.get('NetworkSettings', {}).get('Ports')
        if port_settings is None:
            return None

        if '/' in private_port:
            return port_settings.get(private_port)

        h_ports = port_settings.get(private_port + '/tcp')
        if h_ports is None:
            h_ports = port_settings.get(private_port + '/udp')

        return h_ports

    @utils.check_resource
    @utils.minimum_version('1.20')
    def put_archive(self, container, path, data):
        """
        Insert a file or folder in an existing container using a tar archive as
        source.

        Args:
            container (str): The container where the file(s) will be extracted
            path (str): Path inside the container where the file(s) will be
                extracted. Must exist.
            data (bytes): tar data to be extracted

        Returns:
            (bool): True if the call succeeds.
            :py:class:`~docker.errors.APIError` will be raised if an error
            occurs.
        """
        params = {'path': path}
        url = self._url('/containers/{0}/archive', container)
        res = self._put(url, params=params, data=data)
        self._raise_for_status(res)
        return res.status_code == 200

    @utils.check_resource
    def remove_container(self, container, v=False, link=False, force=False):
        """
        Remove a container. Similar to the ``docker rm`` command.

        Args:
            container (str): The container to remove
            v (bool): Remove the volumes associated with the container
            link (bool): Remove the specified link and not the underlying
                container
            force (bool): Force the removal of a running container (uses
                ``SIGKILL``)
        """
        params = {'v': v, 'link': link, 'force': force}
        res = self._delete(
            self._url("/containers/{0}", container), params=params
        )
        self._raise_for_status(res)

    @utils.minimum_version('1.17')
    @utils.check_resource
    def rename(self, container, name):
        """
        Rename a container. Similar to the ``docker rename`` command.

        Args:
            container (str): ID of the container to rename
            name (str): New name for the container
        """
        url = self._url("/containers/{0}/rename", container)
        params = {'name': name}
        res = self._post(url, params=params)
        self._raise_for_status(res)

    @utils.check_resource
    def resize(self, container, height, width):
        """
        Resize the tty session.

        Args:
            container (str or dict): The container to resize
            height (int): Height of tty session
            width (int): Width of tty session
        """
        params = {'h': height, 'w': width}
        url = self._url("/containers/{0}/resize", container)
        res = self._post(url, params=params)
        self._raise_for_status(res)

    @utils.check_resource
    def restart(self, container, timeout=10):
        """
        Restart a container. Similar to the ``docker restart`` command.

        Args:
            container (str or dict): The container to restart. If a dict, the
                ``Id`` key is used.
            timeout (int): Number of seconds to try to stop for before killing
                the container. Once killed it will then be restarted. Default
                is 10 seconds.
        """
        params = {'t': timeout}
        url = self._url("/containers/{0}/restart", container)
        res = self._post(url, params=params)
        self._raise_for_status(res)

    @utils.check_resource
    def start(self, container, binds=None, port_bindings=None, lxc_conf=None,
              publish_all_ports=None, links=None, privileged=None,
              dns=None, dns_search=None, volumes_from=None, network_mode=None,
              restart_policy=None, cap_add=None, cap_drop=None, devices=None,
              extra_hosts=None, read_only=None, pid_mode=None, ipc_mode=None,
              security_opt=None, ulimits=None):
        """
        Similar to the ``docker start`` command, but doesn't support attach
        options. Use ``.logs()`` to recover ``stdout`` and ``stderr``.

        **Deprecation warning:** For API version > 1.15, it is highly
        recommended to provide host config options in the ``host_config``
        parameter of :py:meth:`~ContainerApiMixin.create_container`.

        Args:
            container (str): The container to start

        Example:

            >>> container = cli.create_container(
            ...     image='busybox:latest',
            ...     command='/bin/sleep 30')
            >>> cli.start(container=container.get('Id'))
        """
        if utils.compare_version('1.10', self._version) < 0:
            if dns is not None:
                raise errors.InvalidVersion(
                    'dns is only supported for API version >= 1.10'
                )
            if volumes_from is not None:
                raise errors.InvalidVersion(
                    'volumes_from is only supported for API version >= 1.10'
                )

        if utils.compare_version('1.15', self._version) < 0:
            if security_opt is not None:
                raise errors.InvalidVersion(
                    'security_opt is only supported for API version >= 1.15'
                )
            if ipc_mode:
                raise errors.InvalidVersion(
                    'ipc_mode is only supported for API version >= 1.15'
                )

        if utils.compare_version('1.17', self._version) < 0:
            if read_only is not None:
                raise errors.InvalidVersion(
                    'read_only is only supported for API version >= 1.17'
                )
            if pid_mode is not None:
                raise errors.InvalidVersion(
                    'pid_mode is only supported for API version >= 1.17'
                )

        if utils.compare_version('1.18', self._version) < 0:
            if ulimits is not None:
                raise errors.InvalidVersion(
                    'ulimits is only supported for API version >= 1.18'
                )

        start_config_kwargs = dict(
            binds=binds, port_bindings=port_bindings, lxc_conf=lxc_conf,
            publish_all_ports=publish_all_ports, links=links, dns=dns,
            privileged=privileged, dns_search=dns_search, cap_add=cap_add,
            cap_drop=cap_drop, volumes_from=volumes_from, devices=devices,
            network_mode=network_mode, restart_policy=restart_policy,
            extra_hosts=extra_hosts, read_only=read_only, pid_mode=pid_mode,
            ipc_mode=ipc_mode, security_opt=security_opt, ulimits=ulimits
        )
        start_config = None

        if any(v is not None for v in start_config_kwargs.values()):
            if utils.compare_version('1.15', self._version) > 0:
                warnings.warn(
                    'Passing host config parameters in start() is deprecated. '
                    'Please use host_config in create_container instead!',
                    DeprecationWarning
                )
            start_config = self.create_host_config(**start_config_kwargs)

        url = self._url("/containers/{0}/start", container)
        res = self._post_json(url, data=start_config)
        self._raise_for_status(res)

    @utils.minimum_version('1.17')
    @utils.check_resource
    def stats(self, container, decode=None, stream=True):
        """
        Stream statistics for a specific container. Similar to the
        ``docker stats`` command.

        Args:
            container (str): The container to stream statistics from
            decode (bool): If set to true, stream will be decoded into dicts
                on the fly. False by default.
            stream (bool): If set to false, only the current stats will be
                returned instead of a stream. True by default.

        """
        url = self._url("/containers/{0}/stats", container)
        if stream:
            return self._stream_helper(self._get(url, stream=True),
                                       decode=decode)
        else:
            return self._result(self._get(url, params={'stream': False}),
                                json=True)

    @utils.check_resource
    def stop(self, container, timeout=10):
        """
        Stops a container. Similar to the ``docker stop`` command.

        Args:
            container (str): The container to stop
            timeout (int): Timeout in seconds to wait for the container to
                stop before sending a ``SIGKILL``. Default: 10
        """
        params = {'t': timeout}
        url = self._url("/containers/{0}/stop", container)

        res = self._post(url, params=params,
                         timeout=(timeout + (self.timeout or 0)))
        self._raise_for_status(res)

    @utils.check_resource
    def top(self, container, ps_args=None):
        """
        Display the running processes of a container.

        Args:
            container (str): The container to inspect
            ps_args (str): An optional arguments passed to ps (e.g. ``aux``)

        Returns:
            (str): The output of the top
        """
        u = self._url("/containers/{0}/top", container)
        params = {}
        if ps_args is not None:
            params['ps_args'] = ps_args
        return self._result(self._get(u, params=params), True)

    @utils.check_resource
    def unpause(self, container):
        """
        Unpause all processes within a container.

        Args:
            container (str): The container to unpause
        """
        url = self._url('/containers/{0}/unpause', container)
        res = self._post(url)
        self._raise_for_status(res)

    @utils.minimum_version('1.22')
    @utils.check_resource
    def update_container(
        self, container, blkio_weight=None, cpu_period=None, cpu_quota=None,
        cpu_shares=None, cpuset_cpus=None, cpuset_mems=None, mem_limit=None,
        mem_reservation=None, memswap_limit=None, kernel_memory=None,
        restart_policy=None
    ):
        """
        Update resource configs of one or more containers.

        Args:
            container (str): The container to inspect
            blkio_weight (int): Block IO (relative weight), between 10 and 1000
            cpu_period (int): Limit CPU CFS (Completely Fair Scheduler) period
            cpu_quota (int): Limit CPU CFS (Completely Fair Scheduler) quota
            cpu_shares (int): CPU shares (relative weight)
            cpuset_cpus (str): CPUs in which to allow execution
            cpuset_mems (str): MEMs in which to allow execution
            mem_limit (int or str): Memory limit
            mem_reservation (int or str): Memory soft limit
            memswap_limit (int or str): Total memory (memory + swap), -1 to
                disable swap
            kernel_memory (int or str): Kernel memory limit
            restart_policy (dict): Restart policy dictionary

        Returns:
            (dict): Dictionary containing a ``Warnings`` key.
        """
        url = self._url('/containers/{0}/update', container)
        data = {}
        if blkio_weight:
            data['BlkioWeight'] = blkio_weight
        if cpu_period:
            data['CpuPeriod'] = cpu_period
        if cpu_shares:
            data['CpuShares'] = cpu_shares
        if cpu_quota:
            data['CpuQuota'] = cpu_quota
        if cpuset_cpus:
            data['CpusetCpus'] = cpuset_cpus
        if cpuset_mems:
            data['CpusetMems'] = cpuset_mems
        if mem_limit:
            data['Memory'] = utils.parse_bytes(mem_limit)
        if mem_reservation:
            data['MemoryReservation'] = utils.parse_bytes(mem_reservation)
        if memswap_limit:
            data['MemorySwap'] = utils.parse_bytes(memswap_limit)
        if kernel_memory:
            data['KernelMemory'] = utils.parse_bytes(kernel_memory)
        if restart_policy:
            if utils.version_lt(self._version, '1.23'):
                raise errors.InvalidVersion(
                    'restart policy update is not supported '
                    'for API version < 1.23'
                )
            data['RestartPolicy'] = restart_policy

        res = self._post_json(url, data=data)
        return self._result(res, True)

    @utils.check_resource
    def wait(self, container, timeout=None):
        """
        Identical to the ``docker wait`` command. Block until a container
        stops, then return its exit code.

        Args:
            container (str or dict): The container to wait on. If a dict, the
                ``Id`` key is used.
            timeout (int): Request timeout

        Returns:
            (int): The exit code of the container. Returns ``-1`` if the API
            responds without a ``StatusCode`` attribute.

        Raises:
            requests.exceptions.ReadTimeout: If the timeout is exceeded.
        """

        url = self._url("/containers/{0}/wait", container)
        res = self._post(url, timeout=timeout)
        self._raise_for_status(res)
        json_ = res.json()
        if 'StatusCode' in json_:
            return json_['StatusCode']
        return -1
