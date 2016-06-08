from .. import utils


class ServiceApiMixin(object):
    @utils.minimum_version('1.24')
    def services(self, filters=None):
        params = {
            'filters': utils.convert_filters(filters) if filters else None
        }
        url = self._url('/services')
        return self._result(self._get(url, params=params), True)

    @utils.minimum_version('1.24')
    def create_service(self, name=None):
        url = self._url('/services/create')
        if driver_opts is not None and not isinstance(driver_opts, dict):
            raise TypeError('driver_opts must be a dictionary')

        data = {
            'Name': name,
            'Driver': driver,
            'DriverOpts': driver_opts,
        }
        return self._result(self._post_json(url, data=data), True)

    @utils.minimum_version('1.24')
    def inspect_service(self, name):
        url = self._url('/services/{0}', name)
        return self._result(self._get(url), True)

    @utils.minimum_version('1.24')
    def remove_service(self, name):
        url = self._url('/services/{0}', name)
        resp = self._delete(url)
        self._raise_for_status(resp)
