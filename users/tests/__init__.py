from rest_framework.test import APITestCase
from django.urls import reverse


class AuthAPI(APITestCase):

    def test_register(self):
        url = reverse('auth-register')

        test_cases = [
            {
                "body": {
                    "password": "123456",
                    "re_password": "123456",
                    "name": "Invalid email format"
                },
                'description': 'Email not provided',
                'status_code': 400
            },
            {
                "body": {
                    "email": "newuser@gmail.com",
                    "re_password": "password456",
                    "name": "Password mismatch"
                },
                'description': 'Password not provided',
                'status_code': 400
            },
            {
                "body": {
                    "email": "newuser@gmail.com",
                    "password": "password123",
                    "name": "Password mismatch"
                },
                'description': 're_password not provided',
                'status_code': 400
            },
            {
                "body": {
                    "email": "newuser@gmail.com",
                    "password": "password123",
                    "re_password": "password456",
                },
                'description': 'Name not provided',
                'status_code': 400
            },
            {
                "body": {
                    "email": "invalid-email-format",
                    "password": "123456",
                    "re_password": "123456",
                    "name": "Invalid email format"
                },
                'description': 'Invalid email format',
                'status_code': 400
            },
            {
                "body": {
                    "email": "newuser@gmail.com",
                    "password": "password123",
                    "re_password": "password456",
                    "name": "Password mismatch"
                },
                'description': 'Password and re_password do not match',
                'status_code': 400
            },
            {
                "body": {
                    "email": "newuser@gmail.com",
                    "password": "password123",
                    "re_password": "password123",
                    "name": "New user"
                },
                'description': 'Register successfully',
                'status_code': 200
            },
            {
                "body": {
                    "email": "newuser@gmail.com",
                    "password": "password123",
                    "re_password": "password123",
                    "name": "New user"
                },
                'description': 'All fields provided correctly',
                'status_code': 400
            }
        ]

        for case in test_cases:
            with self.subTest(case['description']):
                response = self.client.post(url, data=case['body'])
                self.assertEqual(response.status_code, case['status_code'], response.data)

    def test_login(self):
        url = reverse('auth-login')

        # Setup
        self.client.post(reverse('auth-register'), data={
                    "email": "newuser@gmail.com",
                    "password": "password123",
                    "re_password": "password123",
                    "name": "New user"
                })

        test_cases = [
            {
                "body": {
                    "email": "",
                    "password": ""
                },
                'description': 'Email and password not provided',
                'status_code': 400
            },
            {
                "body": {
                    "email": "",
                    "password": "password123"
                },
                'description': 'Email not provided',
                'status_code': 400
            },
            {
                "body": {
                    "email": "newuser@gmail.com",
                    "password": "",
                },
                'description': 'Password not provided',
                'status_code': 400
            },
            {
                "body": {
                    "email": "invalid-email-format",
                    "password": "password123",
                },
                'description': 'Invalid email format',
                'status_code': 400
            },
            {
                "body": {
                    "email": "newuser@gmail.com",
                    "password": "password123",
                },
                'description': 'Login successfully',
                'status_code': 200
            }
        ]

        for case in test_cases:
            with self.subTest(case['description']):
                response = self.client.post(url, data=case['body'])
                self.assertEqual(response.status_code, case['status_code'], case['description'])

    def test_request_token(self):
        url = reverse('auth-request-token')

        test_cases = [
            {
                "body": {
                    "email": ""
                },
                'description': 'Email not provided',
                'status_code': 400
            },
            {
                "body": {
                    "email": "a@gmail.com"
                },
                'description': 'Email not found',
                'status_code': 404
            }]

        for case in test_cases:
            with self.subTest(case['description']):
                response = self.client.post(url, data=case['body'])
                self.assertEqual(response.status_code, case['status_code'], case['description'])

