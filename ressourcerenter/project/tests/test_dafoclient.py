from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from project.dafo import DatafordelerClient



@override_settings(OPENID={'mock': 'cvr'})
class TestStuff(TestCase):

    def test_administration_not_logged_in(self):
        pass
        """
        Stuff
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_company_information('1234')
        # result{'name': 'test company_name'}
        self.assertEqual('test company_name', result.get('name'))



    #def test_user_not_logged_in(self):
        """
        Stuff
        """
        #dafo_client = DatafordelerClient.from_settings()
        #result = dafo_client.get_company_information('1234')
        # print(result)
