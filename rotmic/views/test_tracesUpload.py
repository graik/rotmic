from django.test import TestCase

class TracesUploadTest(TestCase):
    """Upload of Sequencing Traces"""
    fixtures = ['users_test.json', 'rotmic_test.json']
    
    def setUp(self):
        self.client.login(username='raik', password='rotmic')
    
    def test_uploadview_get(self):
        """uploadview get"""
        response = self.client.get('/rotmic/upload/tracefiles/')
        self.assertEqual(response.status_code, 200)
        
    def test_post0files(self):
        """uploadview post 0 files"""
        response = self.client.post('/rotmic/upload/tracefiles/', 
                                    {'evaluation':'none'})
        self.assertEqual(response.status_code, 302) # redirect
    