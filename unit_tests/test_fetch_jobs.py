import unittest
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import re


def clean_job_posting_params(link):
    try:
        parsed = urlparse(link)
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=True)
            # remove the Simplify tracking parameters
            params.pop('utm_source', None)
            params.pop('ref', None)
            # rebuilding the query string
            new_query = urlencode(params, doseq=True)
            # rebuild the URL
            link = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params,
                               new_query, parsed.fragment))
    except Exception as e:
        print(f"The urllib failed we are resulting back to regex: {e}")
        link = re.sub(r'[?&](utm_source|ref)=Simplify', '', link)
        link = re.sub(r'[?&]$', '', link)
    return link


class MyTestCase(unittest.TestCase):
    def test_remove_simplify_params(self):
        test_urls = [
            {
                'input_url': 'https://kiongroup.wd3.myworkdayjobs.com/kion_scs/job/Grand-Rapids-MI-United-States/Software-Engineering-Intern_JR-0082104?utm_source=Simplify&ref=Simplify',
                'output_url': 'https://kiongroup.wd3.myworkdayjobs.com/kion_scs/job/Grand-Rapids-MI-United-States/Software-Engineering-Intern_JR-0082104'
            },
            {
                'input_url': 'https://university-uber.icims.com/jobs/152174/job?mobile=true&needsRedirect=false&utm_source=Simplify&ref=Simplify',
                'output_url': 'https://university-uber.icims.com/jobs/152174/job?mobile=true&needsRedirect=false'
            },
            {
                'input_url': 'https://jobs.bmwgroup.com/job/Mountain-View-Intern,-Digital-Life-Innovation-In-Car-Entertainment-SpringSummer-2026-Cali/1275683401/?ats=successfactors&utm_source=Simplify&ref=Simplify',
                'output_url': 'https://jobs.bmwgroup.com/job/Mountain-View-Intern,-Digital-Life-Innovation-In-Car-Entertainment-SpringSummer-2026-Cali/1275683401/?ats=successfactors'
            }
        ]
        for test_case in test_urls:
            result = clean_job_posting_params(test_case['input_url'])
            self.assertEqual(result, test_case['output_url'])

    def test_url_without_params(self):
        input_url = 'https://example.com/job/12345'
        expected_result = 'https://example.com/job/12345'
        result = clean_job_posting_params(input_url)
        self.assertEqual(result, expected_result)

    def testing_fallback_to_regex(self):
        test_urls = [
            {
                'name': 'Simple Simplify params with ?',
                'input': 'https://example.com/job?utm_source=Simplify&ref=Simplify',
                'expected': 'https://example.com/job'
            },
            {
                'name': 'Simplify params in middle',
                'input': 'https://example.com/job?id=123&utm_source=Simplify&ref=Simplify&other=value',
                'expected': 'https://example.com/job?id=123&other=value'
            },
            {
                'name': 'Only utm_source without ref',
                'input': 'https://example.com/job?utm_source=Simplify&other=value',
                'expected': 'https://example.com/job?other=value'
            },
            {
                'name': 'Only ref without utm_source',
                'input': 'https://example.com/job?id=123&ref=Simplify',
                'expected': 'https://example.com/job?id=123'
            },
            {
                'name': 'Trailing ampersand cleanup',
                'input': 'https://example.com/job?utm_source=Simplify&',
                'expected': 'https://example.com/job'
            }
        ]
        for test_case in test_urls:
            with self.subTest(name=test_case['name']):
                result = test_case['input']
                result = re.sub(r'[?&](utm_source|ref)=Simplify', '', result)
                result = re.sub(r'[?&]$', '', result)
                self.assertEqual(result, test_case['expected'])

if __name__ == '__main__':
    unittest.main()
