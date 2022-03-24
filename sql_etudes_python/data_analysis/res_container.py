class ResContainer:
    """Class used to store analysis results by key.

    The results are stored along with their descriptions. The results can be accesses
    with a key for which they were stored.

    Author: Jernej Vivod (vivod.jernej@gmail.com)
    """

    def __init__(self):
        self._results = dict()

    def add_res_with_desc(self, key, res, desc):
        """Add result for a key with a description

        :param key: key for which to store the results
        :param res: the result value
        :param desc: the description of the result
        """
        self._results[key] = {'res': res, 'desc': desc}

    def get_res(self, key):
        """Get result by key

        :param key: key for the result
        :return: result associated with a key
        """
        return self._results[key]['res']

    def get_desc(self, key):
        """Get description for result by key

        :param key: key for the result
        :return: description of the result
        """
        return self._results[key]['desc']

    def keys(self):
        """Get keys for the results contained in this ResContainer instance

        :return: set of keys contained by this ResContainer instance
        """
        return set(self._results.keys())

    def __str__(self):
        res = ''
        for k, v in self._results.items():
            res += '{0} - {1}\n'.format(k, v['desc'])
        return res
