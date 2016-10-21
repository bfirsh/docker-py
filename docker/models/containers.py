import copy

from ..errors import (ContainerError, ImageNotFound,
                      create_unexpected_kwargs_error)
from .images import Image
from .resource import Collection, Model


class Container(Model):

    @property
    def name(self):
        """
        Returns the name of the container.
        """
        if self.attrs.get('Name') is not None:
            return self.attrs['Name'].lstrip('/')

    @property
    def status(self):
        """
        Returns the status of the container. For example, `running`, or
        `exited`.
        """
        return self.attrs['State']['Status']

    def attach(self, *args, **kwargs):
        return self.client.api.attach(self.id, *args, **kwargs)

    def commit(self, *args, **kwargs):
        resp = self.client.api.commit(self.id, *args, **kwargs)
        return self.client.images.get(resp['Id'])

    def diff(self, *args, **kwargs):
        return self.client.api.diff(self.id, *args, **kwargs)

    def exec_run(self, cmd, stdout=True, stderr=True, stdin=False, tty=False,
                 privileged=False, user='', detach=False, stream=False,
                 socket=False):
        resp = self.client.api.exec_create(
            self.id, cmd, stdout=stdout, stderr=stderr, stdin=stdin, tty=tty,
            privileged=privileged, user=user
        )
        return self.client.api.exec_start(
            resp['Id'], detach=detach, tty=tty, stream=stream, socket=socket
        )

    def export(self, *args, **kwargs):
        return self.client.api.export(self.id, *args, **kwargs)

    def get_archive(self, *args, **kwargs):
        return self.client.api.get_archive(self.id, *args, **kwargs)

    def kill(self, *args, **kwargs):
        return self.client.api.kill(self.id, *args, **kwargs)

    def logs(self, *args, **kwargs):
        return self.client.api.logs(self.id, *args, **kwargs)

    def pause(self, *args, **kwargs):
        return self.client.api.pause(self.id, *args, **kwargs)

    def put_archive(self, *args, **kwargs):
        return self.client.api.put_archive(self.id, *args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.client.api.remove_container(self.id, *args, **kwargs)

    def rename(self, *args, **kwargs):
        return self.client.api.rename(self.id, *args, **kwargs)

    def resize(self, *args, **kwargs):
        return self.client.api.resize(self.id, *args, **kwargs)

    def restart(self, *args, **kwargs):
        return self.client.api.restart(self.id, *args, **kwargs)

    def start(self, *args, **kwargs):
        return self.client.api.start(self.id, *args, **kwargs)

    def stats(self, *args, **kwargs):
        return self.client.api.stats(self.id, *args, **kwargs)

    def stop(self, *args, **kwargs):
        return self.client.api.stop(self.id, *args, **kwargs)

    def top(self, *args, **kwargs):
        return self.client.api.top(self.id, *args, **kwargs)

    def unpause(self, *args, **kwargs):
        return self.client.api.unpause(self.id, *args, **kwargs)

    def update(self, *args, **kwargs):
        return self.client.api.update_container(self.id, *args, **kwargs)

    def wait(self, *args, **kwargs):
        return self.client.api.wait(self.id, *args, **kwargs)


# kwargs to copy straight from run to create
RUN_CREATE_KWARGS = [
    'command',
    # 'cpu_shares', # TODO: pass through for particular version?
    # 'cpuset',
    'detach',
    'domainname',
    'entrypoint',
    'environment',
    'hostname',
    'image',
    'labels',
    'mac_address',
    'name',
    'network_disabled',
    'stdin_open',
    'stop_signal',
    'tty',
    'user',
    'volume_driver',
    # 'volumes_from', # TODO: pass through for particular version?
    'working_dir',
]

# kwargs to copy straight from run to host_config
RUN_HOST_CONFIG_KWARGS = [
    'blkio_weight_device',
    'blkio_weight',
    'cap_add',
    'cap_drop',
    'cgroup_parent',
    'cpu_period',
    'cpu_quota',
    'cpu_shares',
    'cpuset_cpus',
    'device_read_bps',
    'device_read_iops',
    'device_write_bps',
    'device_write_iops',
    'devices',
    'dns_opt',
    'dns_search',
    'dns',  # TODO: moved from create to host_config
    'extra_hosts',
    'group_add',
    'ipc_mode',
    'kernel_memory',
    'links',
    'log_config',
    'lxc_conf',
    'mem_limit',  # TODO: moved from create to host_config
    'mem_reservation',
    'mem_swappiness',
    'memswap_limit',  # TODO: moved from create to host_config
    'network_mode',
    'oom_kill_disable',
    'oom_score_adj',
    'pid_mode',
    'pids_limit',
    'privileged',
    'publish_all_ports',
    'read_only',
    'restart_policy',
    'security_opt',
    'shm_size',
    'sysctls',
    'tmpfs',
    'ulimits',
    'userns_mode',
    'version',
    'volumes_from',
]


class ContainerCollection(Collection):
    model = Container

    def run(self, image, command=None, stdout=True, stderr=False,
            remove=False, **kwargs):
        """
        Run a container. By default, it will wait for the container to finish
        and return its logs, similar to ``docker run``

        If the ``detach`` argument is ``True``, it will start the container
        and immediately return a :py:class:`Container` object, similar to
        ``docker run -d``.

        Args:
            image (str): The image to run.
            command (str or list): The command to run in the container.
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
            detach (bool): Run container in the background and return a
                :py:class:`Container` object.
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
            dns_opt (list): Additional options to be added to the container's
                ``resolv.conf`` file.
            dns_search (list): DNS search domains.
            domainname (str or list): Set custom DNS search domains.
            entrypoint (str or list): The entrypoint for the container.
            environment (dict or list): Environment variables to set inside
                the container, as a dictionary or a list of strings in the
                format ``["SOMEVARIABLE=xxx"]``.
            extra_hosts (dict): Addtional hostnames to resolve inside the
                container, as a mapping of hostname to IP address.
            group_add (list): List of additional group names and/or IDs that
                the container process will run as.
            hostname (str): Optional hostname for the container.
            ipc_mode (str): Set the IPC mode for the container.
            labels (dict or list): A dictionary of name-value labels (e.g.
                ``{"label1": "value1", "label2": "value2"}``) or a list of
                names of labels to set with empty values (e.g.
                ``["label1", "label2"]``)
            links (dict or list of tuples): Either a dictionary mapping name
                to alias or as a list of ``(name, alias)`` tuples.
            log_config (dict): Logging configuration, as a dictionary with
                keys:

                - ``type`` The logging driver name.
                - ``config`` A dictionary of configuration for the logging
                  driver.

            mac_address (str): MAC address to assign to the container.
            mem_limit (float or str): Memory limit. Accepts float values
                (which represent the memory limit of the created container in
                bytes) or a string with a units identification char
                (``100000b``, ``1000k``, ``128m``, ``1g``). If a string is
                specified without a units character, bytes are assumed as an
                intended unit.
            mem_limit (str or int): Maximum amount of memory container is
                allowed to consume. (e.g. ``1G``).
            mem_swappiness (int): Tune a container's memory swappiness
                behavior. Accepts number between 0 and 100.
            memswap_limit (str or int): Maximum amount of memory + swap a
                container is allowed to consume.
            networks (list): A list of network names to connect this
                container to.
            name (str): The name for this container.
            network_disabled (bool): Disable networking.
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
            ports (dict): Ports to bind inside the container.

                The keys of the dictionary are the ports to bind inside the
                container, either as an integer or a string in the form
                ``port/protocol``, where the protocol is either ``tcp`` or
                ``udp``.

                The values of the dictionary are the corresponding ports to
                open on the host, which can be either:

                - The port number, as an integer. For example,
                  ``{'2222/tcp': 3333}`` will expose port 2222 inside the
                  container as port 3333 on the host.
                - ``None``, to assign a random host port. For example,
                  ``{'2222/tcp': None}``.
                - A tuple of ``(address, port)`` if you want to specify the
                  host interface. For example,
                  ``{'1111/tcp': ('127.0.0.1', 1111)}``.
                - A list of integers, if you want to bind multiple host ports
                  to a single container port. For example,
                  ``{'1111/tcp': [1234, 4567]}``.

            privileged (bool): Give extended privileges to this container.
            publish_all_ports (bool): Publish all ports to the host.
            read_only (bool): Mount the container's root filesystem as read
                only.
            remove (bool): Remove the container when it has finished running.
                Default: ``False``.
            restart_policy (dict): Restart the container when it exits.
                Configured as a dictionary with keys:

                - ``Name`` One of ``on-failure``, or ``always``.
                - ``MaximumRetryCount`` Number of times to restart the
                  container on failure.

                For example:
                ``{"Name": "on-failure", "MaximumRetryCount": 5}``

            security_opt (list): A list of string values to customize labels
                for MLS systems, such as SELinux.
            shm_size (str or int): Size of /dev/shm (e.g. ``1G``).
            stdin_open (bool): Keep ``STDIN`` open even if not attached.
            stdout (bool): Return logs from ``STDOUT`` when ``detach=False``.
                Default: ``True``.
            stdout (bool): Return logs from ``STDERR`` when ``detach=False``.
                Default: ``False``.
            stop_signal (str): The stop signal to use to stop the container
                (e.g. ``SIGINT``).
            sysctls (dict): Kernel parameters to set in the container.
            tmpfs (dict): Temporary filesystems to mount, as a dictionary
                mapping a path inside the container to options for that path.

                For example:

                .. code-block:: python

                    {
                        '/mnt/vol2': '',
                        '/mnt/vol1': 'size=3G,uid=1000'
                    }

            tty (bool): Allocate a pseudo-TTY.
            ulimits (list): Ulimits to set inside the container, as a list of
                dicts.
            user (str or int): Username or UID to run commands as inside the
                container.
            userns_mode (str): Sets the user namespace mode for the container
                when user namespace remapping option is enabled. Supported
                values are: ``host``
            volume_driver (str): The name of a volume driver/plugin.
            volumes (dict or list): A dictionary to configure volumes mounted
                inside the container. The key is either the host path or a
                volume name, and the value is a dictionary with the keys:

                - ``bind`` The path to mount the volume inside the container
                - ``mode`` Either ``rw`` to mount the volume read/write, or
                  ``ro`` to mount it read-only.

                For example:

                .. code-block:: python

                    {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
                     '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}

            volumes_from (list): List of container names or IDs to get
                volumes from.
            working_dir (str): Path to the working directory.

        Returns:
            The container logs, either ``STDOUT``, ``STDERR``, or both,
            depending on the value of the ``stdout`` and ``stderr`` arguments.

            If ``detach`` is ``True``, a :py:class:`Container` object is
            returned instead.

        Raises:
            :py:class:`docker.errors.ContainerError`
                If the container exits with a non-zero exit code and
                ``detach`` is ``False``.
            :py:class:`docker.errors.ImageNotFound`
                If the specified image does not exist.
            :py:class:`docker.errors.APIError`
                If there is a server error.
        """
        if isinstance(image, Image):
            image = image.id
        detach = kwargs.pop("detach", False)
        if detach and remove:
            raise RuntimeError("The options 'detach' and 'remove' cannot be "
                               "used together.")

        try:
            container = self.create(image=image, command=command,
                                    detach=detach, **kwargs)
        except ImageNotFound:
            self.client.images.pull(image)
            container = self.create(image=image, command=command,
                                    detach=detach, **kwargs)

        container.start()

        if detach:
            return container

        exit_status = container.wait()
        if exit_status != 0:
            stdout = False
            stderr = True
        out = container.logs(stdout=stdout, stderr=stderr)
        if remove:
            container.remove()
        if exit_status != 0:
            raise ContainerError(container, exit_status, command, image, out)
        return out

    def _build_create_container_args(self, **kwargs):
        """
        Convert arguments to create() to arguments to create_container().
        """
        # Copy over kwargs which can be copied directly
        create_kwargs = {}
        for key in copy.copy(kwargs):
            if key in RUN_CREATE_KWARGS:
                create_kwargs[key] = kwargs.pop(key)
        host_config_kwargs = {}
        for key in copy.copy(kwargs):
            if key in RUN_HOST_CONFIG_KWARGS:
                host_config_kwargs[key] = kwargs.pop(key)

        # Process kwargs which are split over both create and host_config
        ports = kwargs.pop('ports', {})
        if ports:
            host_config_kwargs['port_bindings'] = ports

        volumes = kwargs.pop('volumes', {})
        if volumes:
            host_config_kwargs['binds'] = volumes

        networks = kwargs.pop('networks', [])
        if networks:
            create_kwargs['networking_config'] = {network: None
                                                  for network in networks}

        # All kwargs should have been consumed by this point, so raise
        # error if any are left
        if kwargs:
            raise create_unexpected_kwargs_error('run', kwargs)

        create_kwargs['host_config'] = self.client.api.create_host_config(
            **host_config_kwargs)

        # Fill in any kwargs which need processing by create_host_config first
        port_bindings = create_kwargs['host_config'].get('PortBindings')
        if port_bindings:
            # sort to make consistent for tests
            create_kwargs['ports'] = [tuple(p.split('/', 1))
                                      for p in sorted(port_bindings.keys())]
        binds = create_kwargs['host_config'].get('Binds')
        if binds:
            create_kwargs['volumes'] = [v.split(':')[0] for v in binds]
        return create_kwargs

    def create(self, image, command=None, **kwargs):
        """
        Create a container without starting it. Similar to ``docker create``.

        Takes the same arguments as :py:meth:`run`, except for ``stdout``,
        ``stderr``, and ``remove``.

        Returns:
            A :py:class:`Container` object.

        Raises:
            :py:class:`docker.errors.ImageNotFound`
                If the specified image does not exist.
            :py:class:`docker.errors.APIError`
                If there is a server error.
        """
        if isinstance(image, Image):
            image = image.id
        create_kwargs = self._build_create_container_args(image=image,
                                                          command=command,
                                                          **kwargs)
        resp = self.client.api.create_container(**create_kwargs)
        return self.get(resp['Id'])

    def get(self, container_id):
        """
        Get a container by name or ID.

        Returns:
            A :py:class:`Container` object.
        """
        resp = self.client.api.inspect_container(container_id)
        return self.prepare_model(resp)

    def list(self, all=False, before=None, filters=None, limit=-1, since=None):
        """
        List containers.

        Returns:
            A list of :py:class:`Container` objects.
        """
        resp = self.client.api.containers(all=all, before=before,
                                          filters=filters, limit=limit,
                                          since=since)
        return [self.get(r['Id']) for r in resp]
