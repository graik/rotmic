from django.test import TestCase

class TracesUploadTest(TestCase):
    """Upload of Sequencing Traces"""
    fixtures = ['users_test.json', 'rotmic_test.json']
    
    def setUp(self):
        self.client.login(username='raik', password='rotmic')
    
    def test_uploadview_get(self):
        """uploadview get"""
        response = self.client.get('/rotmic/attach/sequencing/')
        self.assertEqual(response.status_code, 200)

    