import pandas as pd


class DimensionsImporter(object):

    """docstring for DimensionsImporter"""

    def __init__(self, **kwargs):
        input_file = kwargs.pop('flat_file', None)
        if input_file != None:
            self.demographic_data = pd.read_excel(
                input_file, 'Sheet1')
        else:
            self.demographic_data = pd.DataFrame()

    def demographic_data():
        doc = "The demographic_data property."

        def fget(self):
            return self._demographic_data

        def fset(self, value):
            value = value.rename(columns={'cm_pid': 'respondent_id'})
            if 'respondent_id' in value.columns:
                value = value[value.respondent_id.notnull()]
            value.fillna("", inplace=True)
            self._demographic_data = value

        def fdel(self):
            del self._demographic_data
        return locals()
    demographic_data = property(**demographic_data())
