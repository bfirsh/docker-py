import json

from ..errors import InvalidVersion
from ..utils import check_resource, minimum_version
from ..utils import version_lt


class NetworkApiMixin(object):
    @minimum_version('1.21')
    def networks(self, names=None, ids=None):
        """
        List networks currently registered by the docker daemon. Similar to the ``docker networks ls`` command.

        Args:
            names (list): List of names to filter by
            ids (list): List of ids to filter by

        Returns:
            (dict): List of network objects.
        """

        filters = {}
        if names:
            filters['name'] = names
        if ids:
            filters['id'] = ids

        params = {'filters': json.dumps(filters)}

        url = self._url("/networks")
        res = self._get(url, params=params)
        return self._result(res, json=True)

    @minimum_version('1.21')
    def create_network(self, name, driver=None, options=None, ipam=None,
                       check_duplicate=None, internal=False, labels=None,
                       enable_ipv6=False):
        """
        Create a network, similar to the ``docker network create`` command. See the [networks documentation](networks.md) for details.

        Args:
            name (str): Name of the network
            driver (str): Name of the driver used to create the network
            options (dict): Driver options as a key-value dictionary
            ipam (dict): Optional custom IP scheme for the network
            check_duplicate (bool): Request daemon to check for networks with same name. Default: ``True``.
            internal (bool): Restrict external access to the network. Default ``False``.
            labels (dict): Map of labels to set on the network. Default ``None``.
            enable_ipv6 (bool): Enable IPv6 on the network. Default ``False``.

        Returns:
            (dict): The created network reference object
        """
        if options is not None and not isinstance(options, dict):
            raise TypeError('options must be a dictionary')

        data = {
            'Name': name,
            'Driver': driver,
            'Options': options,
            'IPAM': ipam,
            'CheckDuplicate': check_duplicate
        }

        if labels is not None:
            if version_lt(self._version, '1.23'):
                raise InvalidVersion(
                    'network labels were introduced in API 1.23'
                )
            if not isinstance(labels, dict):
                raise TypeError('labels must be a dictionary')
            data["Labels"] = labels

        if enable_ipv6:
            if version_lt(self._version, '1.23'):
                raise InvalidVersion(
                    'enable_ipv6 was introduced in API 1.23'
                )
            data['EnableIPv6'] = True

        if internal:
            if version_lt(self._version, '1.22'):
                raise InvalidVersion('Internal networks are not '
                                     'supported in API version < 1.22')
            data['Internal'] = True

        url = self._url("/networks/create")
        res = self._post_json(url, data=data)
        return self._result(res, json=True)

    @minimum_version('1.21')
    def remove_network(self, net_id):
        """
        Remove a network. Similar to the ``docker network rm`` command.

        Args:
            net_id (str): The network's id
        """
        url = self._url("/networks/{0}", net_id)
        res = self._delete(url)
        self._raise_for_status(res)

    @minimum_version('1.21')
    def inspect_network(self, net_id):
        """
        Get detailed information about a network.

        Args:
            net_id (str): ID of network
        """
        url = self._url("/networks/{0}", net_id)
        res = self._get(url)
        return self._result(res, json=True)

    @check_resource
    @minimum_version('1.21')
    def connect_container_to_network(self, container, net_id,
                                     ipv4_address=None, ipv6_address=None,
                                     aliases=None, links=None,
                                     link_local_ips=None):
        """
        Connect a container to a network.

        Args:
            container (str): container-id/name to be connected to the network
            net_id (str): network id
            aliases (list): A list of aliases for this endpoint. Names in that list can be used within the network to reach the container. Defaults to ``None``.
            links (list): A list of links for this endpoint. Containers declared in this list will be [linked](https://docs.docker.com/engine/userguide/networking/work-with-networks/#linking-containers-in-user-defined-networks) to this container. Defaults to ``None``.
            ipv4_address (str): The IP address of this container on the network, using the IPv4 protocol. Defaults to ``None``.
            ipv6_address (str): The IP address of this container on the network, using the IPv6 protocol. Defaults to ``None``.
            link_local_ips (list): A list of link-local (IPv4/IPv6) addresses.
        """
        data = {
            "Container": container,
            "EndpointConfig": self.create_endpoint_config(
                aliases=aliases, links=links, ipv4_address=ipv4_address,
                ipv6_address=ipv6_address, link_local_ips=link_local_ips
            ),
        }

        url = self._url("/networks/{0}/connect", net_id)
        res = self._post_json(url, data=data)
        self._raise_for_status(res)

    @check_resource
    @minimum_version('1.21')
    def disconnect_container_from_network(self, container, net_id,
                                          force=False):
        """
        Disconnect a container from a network.

        Args:
            container (str): container ID or name to be disconnected from the network
            net_id (str): network ID
            force (bool): Force the container to disconnect from a network. Default: ``False``
        """
        data = {"Container": container}
        if force:
            if version_lt(self._version, '1.22'):
                raise InvalidVersion(
                    'Forced disconnect was introduced in API 1.22'
                )
            data['Force'] = force
        url = self._url("/networks/{0}/disconnect", net_id)
        res = self._post_json(url, data=data)
        self._raise_for_status(res)
